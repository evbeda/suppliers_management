from datetime import (
    date,
    timedelta,
)
from freezegun import freeze_time
from http import HTTPStatus
from os import (
    path,
)
from parameterized import parameterized
from shutil import rmtree
from unittest.mock import (
    MagicMock,
    patch,
)

from django.conf import settings
from django.contrib.auth.models import Group
from django.core import mail
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.core.urlresolvers import (
    reverse,
    reverse_lazy,
)
from django.db import DatabaseError
from django.http import (
    QueryDict
)
from django.test import (
    Client,
    RequestFactory,
    TestCase,
)
from django.utils import timezone
from django.utils.datastructures import MultiValueDict

from supplier_app.constants.custom_messages import (
    COMPANY_ERROR_MESSAGE,
    EMAIL_ERROR_MESSAGE,
    EMAIL_SUCCESS_MESSAGE,
    JOIN_COMPANY_ERROR_MESSAGE,
    TAXPAYER_CREATION_SUCCESS_MESSAGE,
    TAXPAYER_CREATION_ERROR_MESSAGE,
    TAXPAYER_FORM_INVALID_MESSAGE,
    TAXPAYER_NOT_EXISTS_MESSAGE,
)
from supplier_app import (
    email_notifications,
    TAXPAYER_STATUS,
)
from supplier_app.forms import (
    AddressCreateForm,
    BankAccountCreateForm,
    TaxPayerCreateForm,
    TaxPayerEditForm,
)
from supplier_app.models import (
    Address,
    BankAccount,
    Company,
    CompanyUniqueToken,
    TaxPayer,
    TaxPayerArgentina,
    TaxpayerComment,
)
from supplier_app.tests import (
    taxpayer_creation_POST_factory,
    taxpayer_edit_POST_factory,
    get_bank_info_example,
    STATUS_CHANGE_REQUIRED,
    STATUS_PENDING,
    BUSINESS_EXAMPLE_NAME_1,
    BUSINESS_EXAMPLE_NAME_2,
    TOKEN_COMPANY
)
from supplier_app.tests.factory_boy import (
    AddressFactory,
    BankAccountFactory,
    CompanyFactory,
    CompanyUniqueTokenFactory,
    CompanyUserPermissionFactory,
    EBEntityFactory,
    TaxPayerArgentinaFactory,
)
from supplier_app.views import (
    CreateTaxPayerView,
    CompanyUserPermission,
    EditTaxpayerView,
    SupplierHome,
)
from utils.exceptions import CouldNotSendEmailError
from users_app.models import User
from users_app.factory_boy import (
    UserFactory,
    ApUserFactory,
)


class TestCreateTaxPayer(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.file_mock = MagicMock(spec=File)
        self.file_mock.name = 'test.pdf'
        self.file_mock.size = 50
        self.bank_info = get_bank_info_example("CITIBANK N.A.")
        self.create_taxpayer_view = CreateTaxPayerView()
        self.company = CompanyFactory(
            name='FakeCompany',
            description='Best catering worldwide'
        )
        self.supplier_group = Group.objects.get(name='supplier')
        self.user_with_eb_social = UserFactory(email='nicolas')
        self.user_with_eb_social.groups.add(self.supplier_group)
        self.client.force_login(self.user_with_eb_social)
        self.companyuserpermission = CompanyUserPermissionFactory(
            company=self.company,
            user=self.user_with_eb_social
        )
        self.POST = taxpayer_creation_POST_factory(
            afip_file=self.file_mock,
            bank_info=self.bank_info,
        )

    def tearDown(self):
        if self.file_mock and path.exists(
            'file/{}'.format(self.file_mock.name)
        ):
            rmtree('file')

    def _get_example_forms(self, **kwargs):
        eb_entities = []
        if 'eb_entities' in kwargs:
            for eb_entity in kwargs['eb_entities']:
                eb_entities.append(str(eb_entity.id))
        else:
            eb_entities.append(str(EBEntityFactory().id))
        FORM_POST = QueryDict('', mutable=True)
        FORM_POST.update(self.POST)
        FORM_POST.setlist(
            'taxpayer_form-eb_entities',
            eb_entities,
        )
        forms = {
            'address_form': AddressCreateForm(data=FORM_POST),
            'bankaccount_form': BankAccountCreateForm(
                data=FORM_POST,
                files=self._get_request_FILES()
            ),
            'taxpayer_form': TaxPayerCreateForm(
                data=FORM_POST,
                files=self._get_request_FILES()
                )
        }
        return forms

    def _get_request_FILES(
        self,
        afip_file=None,
        witholding_taxes_file=None,
        bank_cbu_file=None
    ):
        return MultiValueDict({
            'taxpayer_form-afip_registration_file': [
                afip_file or self.file_mock
            ],
            'taxpayer_form-witholding_taxes_file': [
                witholding_taxes_file or self.file_mock
            ],
            'bankaccount_form-bank_cbu_file': [
                bank_cbu_file or self.file_mock
            ],
        })

    def test_get_success_url_should_redirect_to_home(self):
        self.assertEqual(
            '/suppliersite/supplier',
            self.create_taxpayer_view.get_success_url()
            )

    def _taxpayer_creation_request(self):
        eb_entity = EBEntityFactory()
        request = self.factory.post(
            '/suppliersite/supplier/taxpayer/create',
            data=taxpayer_creation_POST_factory(eb_entity.id),
            )
        request.user = self.user_with_eb_social
        return request

    @patch('supplier_app.views.messages.add_message')
    def test_form_valid_method_should_save_taxpayer_address_bankaccount(self, msg_mocked):
        taxpayer_qty_before_creation = len(TaxPayer.objects.all())
        bank_account_qty_before_creation = len(BankAccount.objects.all())
        address_qty_before_creation = len(Address.objects.all())
        taxpayer_creation_forms = self._get_example_forms()

        self.create_taxpayer_view.request = \
            self._taxpayer_creation_request()
        self.create_taxpayer_view.form_valid(taxpayer_creation_forms)

        taxpayer_qty_after_creation = len(TaxPayer.objects.all())
        bank_account_qty_after_creation = len(BankAccount.objects.all())
        address_qty_after_creation = len(Address.objects.all())

        self.assertGreater(
            taxpayer_qty_after_creation,
            taxpayer_qty_before_creation
        )
        self.assertGreater(
            bank_account_qty_after_creation,
            bank_account_qty_before_creation
        )
        self.assertGreater(
            address_qty_after_creation,
            address_qty_before_creation
        )

    @patch('supplier_app.views.messages.add_message')
    def test_address_bankaccount_should_be_related_with_taxpayer(self, msg_mocked):
        taxpayer_creation_forms = self._get_example_forms()

        self.create_taxpayer_view.request = \
            self._taxpayer_creation_request()
        self.create_taxpayer_view.form_valid(taxpayer_creation_forms)
        address = Address.objects.last()
        bankaccount = BankAccount.objects.last()
        taxpayer_created = TaxPayer.objects.last()
        self.assertEqual(
            taxpayer_created,
            address.taxpayer
        )
        self.assertEqual(
            taxpayer_created,
            bankaccount.taxpayer
        )

    @patch('supplier_app.views.messages.add_message')
    def test_new_taxpayer_should_be_related_with_3_eb_entities(self, msg_mocked):
        eb_entities = [EBEntityFactory(), EBEntityFactory(), EBEntityFactory()]
        taxpayer_creation_forms = self._get_example_forms(eb_entities=eb_entities)

        self.create_taxpayer_view.request = \
            self._taxpayer_creation_request()
        self.create_taxpayer_view.form_valid(taxpayer_creation_forms)
        taxpayer_created = TaxPayer.objects.last()

        self.assertEqual(3, len(taxpayer_created.taxpayerebentity_set.all()))

    @patch('supplier_app.views.messages.add_message')
    def test_multiple_equal_eb_entities_when_create_taxpayer_should_fail(self, msg_mocked):
        eb_1 = EBEntityFactory()
        eb_2 = EBEntityFactory()
        eb_entities = [eb_1, eb_2, eb_1]
        taxpayer_creation_forms = self._get_example_forms(eb_entities=eb_entities)

        self.create_taxpayer_view.request = \
            self._taxpayer_creation_request()
        self.create_taxpayer_view.form_valid(taxpayer_creation_forms)
        taxpayer_created = TaxPayer.objects.last()

        eb_entities_related_with_taxpayer = \
            [e.eb_entity for e in taxpayer_created.taxpayerebentity_set.all()]
        self.assertEqual(2, len(taxpayer_created.taxpayerebentity_set.all()))
        self.assertIn(eb_1, eb_entities_related_with_taxpayer)
        self.assertIn(eb_2, eb_entities_related_with_taxpayer)

    def test_logged_in_supplier_can_create_taxpayer(self):

        response = self.client.get(
            reverse('taxpayer-create'),
        )

        self.assertIn(
            'supplier_app/taxpayer-creation.html',
            response.template_name,
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK
        )
        self.assertTrue(
            self.user_with_eb_social.groups.filter(name='supplier').exists()
        )

    def test_not_logged_in_supplier_cant_create_taxpayer(self):
        client = Client()
        supplier_user = UserFactory()
        supplier_user.groups.add(self.supplier_group)

        response = client.get(
            reverse('taxpayer-create'),
            follow=True
        )
        self.assertIn(
            'registration/login.html',
            response.template_name,
        )
        self.assertNotIn(
            'supplier_app/taxpayer-creation.html',
            response.template_name
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK
        )
        self.assertTrue(
            supplier_user.groups.filter(name='supplier').exists()
        )

    def test_users_without_required_permission_cant_create(self):
        client = Client()
        user_without_supplier_permission = UserFactory(email='ap@eventbrite.com')
        ap_group = Group.objects.get(name='ap_admin')
        user_without_supplier_permission.groups.add(ap_group)

        client.force_login(user_without_supplier_permission)
        response = client.get(
            reverse('taxpayer-create'),
            follow=True,
        )
        self.assertIn(
            'AP_app/ap-taxpayers.html',
            response.template_name,
        )
        self.assertNotIn(
            'supplier_app/taxpayer-creation.html',
            response.template_name
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK
        )
        self.assertFalse(
            user_without_supplier_permission.groups.filter(name='supplier').exists()
        )


class TestSupplierHome(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

        self.company = CompanyFactory(
            name='Supra',
            description='Best catering worldwide'
        )
        self.taxpayer_ar = TaxPayerArgentinaFactory(
            business_name='Eventbrite',
            workday_id='12345',
            taxpayer_state='PENDING',
            cuit='20-31789965-3',
            company=self.company,
        )

        self.user_with_social_evb = UserFactory(email='nahuel')

        self.company_user_permission = CompanyUserPermissionFactory(
            company=self.company,
            user=self.user_with_social_evb
        )

        self.client = Client()
        self.supplier_user = UserFactory(email='nahuel.valencia21@gmail.com')
        self.supplier_group = Group.objects.get(name='supplier')
        self.supplier_user.groups.add(self.supplier_group)

        self.supplier_home_url = 'supplier-home'

    def test_get_taxpayers_child(self):
        request = self.factory.get('/suppliersite/home')
        request.user = self.user_with_social_evb

        supplier_home = SupplierHome()
        supplier_home.request = request
        taxpayer_list = supplier_home.get_taxpayers()

        self.assertEqual(
            type(taxpayer_list[0]),
            TaxPayerArgentina
        )
        self.assertGreaterEqual(len(taxpayer_list), 1)

    def test_logged_in_supplier_can_access_supplier_home(self):

        self.client.force_login(self.supplier_user)
        response = self.client.get(
            reverse(self.supplier_home_url),
        )

        self.assertIn(
            'supplier_app/supplier-home.html',
            response.template_name,
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK
        )
        self.assertTrue(
            self.supplier_user.groups.filter(name='supplier').exists()
        )

    def test_not_logged_in_supplier_cant_access_supplier_home(self):

        response = self.client.get(
            reverse(self.supplier_home_url),
            follow=True
        )
        self.assertIn(
            'registration/login.html',
            response.template_name,
        )
        self.assertNotIn(
            'supplier_app/supplier-home.html',
            response.template_name
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK
        )
        self.assertTrue(
            self.supplier_user.groups.filter(name='supplier').exists()
        )

    def test_users_without_required_permission_cant_access_supplier_home(self):
        user_without_supplier_permission = UserFactory(email='ap@eventbrite.com')
        ap_group = Group.objects.get(name='ap_admin')
        user_without_supplier_permission.groups.add(ap_group)

        self.client.force_login(user_without_supplier_permission)
        response = self.client.get(
            reverse(self.supplier_home_url),
            follow=True,
        )
        self.assertIn(
            'AP_app/ap-taxpayers.html',
            response.template_name,
        )
        self.assertNotIn(
            'supplier_app/supplier-home.html',
            response.template_name
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK
        )
        self.assertFalse(
            user_without_supplier_permission.groups.filter(name='supplier').exists()
        )


class TestApTaxpayers(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()

        self.ap_home_url = 'ap-taxpayers'

        self.company1 = CompanyFactory(
            name='Empresa 1',
            description='Descripcion de la empresa 1'
        )
        self.company2 = CompanyFactory(
            name='Empresa 2',
            description='Descripcion de la empresa 2'
        )
        self.taxpayer_ar1 = TaxPayerArgentinaFactory(
            business_name=BUSINESS_EXAMPLE_NAME_1,
            workday_id='1',
            taxpayer_state=STATUS_PENDING,
            cuit='20-31789965-3',
            company=self.company1,
        )
        self.taxpayer_ar2 = TaxPayerArgentinaFactory(
            business_name=BUSINESS_EXAMPLE_NAME_2,
            workday_id='2',
            taxpayer_state=STATUS_CHANGE_REQUIRED,
            cuit='20-39237968-5',
            company=self.company2,
        )

        self.user_ap = User.objects.create_user(email='ap@eventbrite.com')
        self.user_ap.groups.add(Group.objects.get(name='ap_admin'))

        self.user_with_social_evb1 = UserFactory(email='nahuel')
        self.user_with_social_evb1.groups.add(Group.objects.get(name='supplier'))
        self.user_with_social_evb2 = UserFactory(email='nicolas')

        self.company_user_permission1 = CompanyUserPermissionFactory(
            company=self.company1,
            user=self.user_with_social_evb1
        )
        self.company_user_permission2 = CompanyUserPermissionFactory(
            company=self.company2,
            user=self.user_with_social_evb2
        )

    @parameterized.expand([
        (
            'taxpayer_state={}&taxpayer_state={}'.format(STATUS_PENDING, STATUS_CHANGE_REQUIRED),
            [BUSINESS_EXAMPLE_NAME_1, BUSINESS_EXAMPLE_NAME_2],
            [],
        ),
        (
           'taxpayer_state={}'.format(STATUS_PENDING),
           [BUSINESS_EXAMPLE_NAME_1],
           [BUSINESS_EXAMPLE_NAME_2],
        ),
        (
            'taxpayer_state={}'.format(STATUS_CHANGE_REQUIRED),
            [BUSINESS_EXAMPLE_NAME_2],
            [BUSINESS_EXAMPLE_NAME_1],
        ),
        (
            'country=AR',
            [BUSINESS_EXAMPLE_NAME_1, BUSINESS_EXAMPLE_NAME_2],
            [],
        ),
    ])
    def test_get_taxpayers_with_filters(
        self,
        query_param,
        contain_business_name,
        not_contain_business_name,
    ):
        self.client.force_login(self.user_ap)
        response = self.client.get(
            "{}?{}".format(reverse(self.ap_home_url), query_param)
        )
        for contain_bn in contain_business_name:
            self.assertContains(response, contain_bn)
        for not_contain_bn in not_contain_business_name:
            self.assertNotContains(response, not_contain_bn)

    def test_get_taxpayers_between_2_dates_in_ap_site(self):
        self.client.force_login(self.user_ap)
        with freeze_time(time_to_freeze=date(2019, 10, 21)):
            taxpayer_21_october = TaxPayerArgentinaFactory()
            taxpayer_21_october2 = TaxPayerArgentinaFactory()
        response = self.client.get(
            '{}?taxpayer_date_after=10/20/2019&taxpayer_date_before=10/22/2019'.format(
                reverse(self.ap_home_url)
            )
        )
        self.assertContains(response, taxpayer_21_october.business_name)
        self.assertContains(response, taxpayer_21_october2.business_name)

    def test_taxpayer_list_show_CUIT_status_and_business_name(self):
        self.client.force_login(self.user_ap)
        response = self.client.get(reverse(self.ap_home_url))
        self.assertContains(response, self.taxpayer_ar1.business_name)
        self.assertContains(response, self.taxpayer_ar2.business_name)
        self.assertContains(response, self.taxpayer_ar1.cuit)
        self.assertContains(response, self.taxpayer_ar2.cuit)
        self.assertContains(response, self.taxpayer_ar1.taxpayer_state)
        self.assertContains(response, self.taxpayer_ar2.taxpayer_state)

    def test_get_all_taxpayers_list_as_ap(self):
        self.client.force_login(self.user_ap)
        response = self.client.get(reverse(self.ap_home_url))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual('AP_app/ap-taxpayers.html', response.template_name[0])

    def test_get_all_taxpayers_list_as_supplier_redirects_to_supplier_home(self):
        self.client.force_login(self.user_with_social_evb1)
        response = self.client.get(
            reverse(self.ap_home_url),
            follow=True
        )
        self.assertEqual('supplier_app/supplier-home.html', response.template_name[0])
        self.assertEqual(response.status_code, HTTPStatus.OK)


class TestSupplierDetailsView(TestCase):

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

        self.file_mock = MagicMock(spec=File)
        self.file_mock.name = 'test.pdf'
        self.file_mock.size = 50

        self.ap_user = User.objects.create_user(email='ap@eventbrite.com')
        self.ap_user.groups.add(Group.objects.get(name='ap_admin'))
        self.client.force_login(self.ap_user)

        self.company_user_permission = CompanyUserPermissionFactory()

        self.taxpayer = TaxPayerArgentinaFactory(
            company=self.company_user_permission.company,
            afip_registration_file=self.file_mock,
            witholding_taxes_file=self.file_mock,
        )
        self.address = AddressFactory(taxpayer=self.taxpayer)
        self.bank_account = BankAccountFactory(
            taxpayer=self.taxpayer,
            bank_cbu_file=self.file_mock
            )

        self.kwargs = {
            'taxpayer_id': self.taxpayer.id,
        }

        self.sup_detail_url = reverse_lazy(
            'supplier-details',
            kwargs=self.kwargs
        )

    def test_get_taxpayers_details_in_ap_site(self):
        response = self.client.get(
            self.sup_detail_url,
        )

        self.assertEqual(
            self.taxpayer,
            response.context_data['taxpayer']
        )
        self.assertEqual(
            self.taxpayer,
            response.context_data['taxpayer_address'].taxpayer
        )
        self.assertEqual(
            self.taxpayer,
            response.context_data['taxpayer_bank_account'].taxpayer
        )

    def test_get_taxpayers_details_success(self):
        response = self.client.get(
            self.sup_detail_url,
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_get_404_when_try_to_get_taxpayer_details_with_invalid_id(self):
        self.client.force_login(self.ap_user)
        response = self.client.get(
            reverse('supplier-details', kwargs={'taxpayer_id': 999}),
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_taxpayer_detail_template(self):
        self.client.force_login(self.ap_user)
        response = self.client.get(
            self.sup_detail_url,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response,
            "CBU"
        )
        self.assertContains(
            response,
            'AFIP certificate'
        )
        self.assertContains(
            response,
            'Withholding taxes'
        )

    def test_details_view_has_approve_button_when_AP_has_set_workday_id(self):
        response = self.client.get(self.sup_detail_url)

        self.assertContains(
            response, 'Approve'
        )

    def test_details_view_doesnt_have_approve_button_when_AP_hasnt_set_workday_id(self):
        taxpayer = TaxPayerArgentinaFactory(
            workday_id="",
            afip_registration_file=self.file_mock,
            witholding_taxes_file=self.file_mock,
        )
        AddressFactory(taxpayer=taxpayer)
        BankAccountFactory(
            taxpayer=taxpayer,
            bank_cbu_file=self.file_mock
        )
        self.client.force_login(self.ap_user)

        response = self.client.get(
            reverse("supplier-details", kwargs={'taxpayer_id': taxpayer.id})
        )

        self.assertNotContains(
            response, 'Approve',
        )

    def test_taxpayer_details_view_doesnt_show_edit_button_when_the_taxpayer_has_status_denied(self):
        taxpayer = TaxPayerArgentinaFactory(
            taxpayer_state="DENIED",
            afip_registration_file=self.file_mock,
            witholding_taxes_file=self.file_mock,
        )
        AddressFactory(taxpayer=taxpayer)
        BankAccountFactory(
            taxpayer=taxpayer,
            bank_cbu_file=self.file_mock
        )
        self.client.force_login(self.ap_user)

        response = self.client.get(
            reverse("supplier-details", kwargs={'taxpayer_id': taxpayer.id})
        )

        self.assertNotContains(
            response, 'Edit',
        )

    @parameterized.expand([
        ("APPROVE", "1"),
        ("DENIED", "2"),
        ("DENIED", ""),
    ])
    def test_taxpayer_details_view_doesnt_show_approve_and_deny_btn_if_taxpayer_is_already_approved_or_denied(
        self,
        status,
        workday_id
    ):
        taxpayer = TaxPayerArgentinaFactory(
            taxpayer_state=status,
            workday_id=workday_id,
            afip_registration_file=self.file_mock,
            witholding_taxes_file=self.file_mock,
        )
        AddressFactory(taxpayer=taxpayer)
        BankAccountFactory(
            taxpayer=taxpayer,
            bank_cbu_file=self.file_mock
        )

        self.client.force_login(self.ap_user)
        response = self.client.get(
            reverse("supplier-details", kwargs={'taxpayer_id': taxpayer.id})
        )

        self.assertNotContains(
            response, 'Approve'
        )

        self.assertNotContains(
            response, 'Deny'
        )


class TestTaxpayerDetailsSupplier(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_sup = UserFactory(email="nicolas.nunez@gmail.com")
        self.user_sup.groups.add(Group.objects.get(name='supplier'))
        self.client.force_login(self.user_sup)
        self.supplier_detail_url = 'supplier-details'
        self.file_mock = MagicMock(spec=File)
        self.file_mock.name = 'test.pdf'
        self.file_mock.size = 50
        self.company = CompanyFactory(
            name='FakeCompany',
            description='Best catering worldwide'
        )
        self.companyuserpermission = CompanyUserPermissionFactory(
            company=self.company,
            user=self.user_sup
        )
        self.taxpayer_example = TaxPayerArgentinaFactory(
            afip_registration_file=self.file_mock,
            witholding_taxes_file=self.file_mock,
            company=self.company,
        )
        self.bank_info_example = BankAccountFactory(
            taxpayer=self.taxpayer_example,
            bank_cbu_file=self.file_mock
            )
        self.addres_example = AddressFactory(taxpayer=self.taxpayer_example)
        self.kwargs = {
            'taxpayer_id': self.taxpayer_example.id
        }

    def _get_taxpayer_detail_response(self):
        return self.client.get(
            reverse(
                self.supplier_detail_url,
                kwargs=self.kwargs
                ),
        )

    def test_taxpayer_detail_view_as_supplier_render_correct_html(self):
        response = self._get_taxpayer_detail_response()
        self.assertIn('AP_app/ap-taxpayer-details.html', response.template_name)

    def test_taxpayer_detail_view_as_supplier_dont_show_approve_denied_btn(self):
        response = self._get_taxpayer_detail_response()
        self.assertNotContains(response, "Approve")
        self.assertNotContains(response, "Deny")


class TestEditTaxPayerInfo(TestCase):
    def setUp(self):
        self.client = Client()
        self.client2 = Client()

        self.ap_group = Group.objects.get(name="ap_admin")
        self.ap_user = UserFactory(email='ap@eventbrite.com')
        self.ap_user.groups.add(self.ap_group)
        self.client.force_login(self.ap_user)

        self.supplier_group = Group.objects.get(name="supplier")
        self.supplier_user = UserFactory(email='nahuelSupplier@gmail.com')
        self.supplier_user.groups.add(self.supplier_group)
        self.client2.force_login(self.supplier_user)

        self.taxpayer = TaxPayerArgentinaFactory()
        self.company_user_permission = CompanyUserPermissionFactory(
            user=self.supplier_user,
            company=self.taxpayer.company
        )
        self.taxpayer_detail_url = 'supplier-details'
        self.taxpayer_edit_url = 'taxpayer-update'
        self.edit_taxpayer_view = EditTaxpayerView()

        self.eb_entity = EBEntityFactory()
        self.TAXPAYER_POST = taxpayer_edit_POST_factory(self.eb_entity.id)
        self.kwargs = {
            'taxpayer_id': self.taxpayer.id,
        }
        self.taxpayer_id = self.taxpayer.id

    def test_get_success_url_should_redirect_to_details_view_when_click_in_update_button(self):
        response = self.client.get(
            reverse(
                self.taxpayer_edit_url,
                kwargs=self.kwargs
            ),
        )

        self.assertEqual(
            'AP_app/edit-taxpayer-information.html',
            response.template_name[0]
        )

    def test_post_edit_taxpayer_info(self):
        response = self.client.post(
            reverse(
                self.taxpayer_edit_url,
                kwargs=self.kwargs
            ),
            data=self.TAXPAYER_POST
        )

        self.assertEqual(
            reverse(
                self.taxpayer_detail_url,
                kwargs=self.kwargs
            ),
            response.url
        )

    def test_post_edit_taxpayer_info_as_supplier_should_redirect_to_supplier_home(self):
        response = self.client2.post(
            reverse(
                self.taxpayer_edit_url,
                kwargs=self.kwargs
            ),
            data=self.TAXPAYER_POST
        )
        self.assertEqual(
            reverse_lazy(
                self.taxpayer_detail_url,
                kwargs=self.kwargs,
            ),
            response.url
        )

    @parameterized.expand([
        (
            taxpayer_edit_POST_factory(
                eb_entity="1",
                workday_id="1",
                business_name="EB US",
                cuit="20-3123214-1",
            ),
            ["workday_id", "business_name", "cuit"],
            ["1", "EB US", "20-3123214-1"]
        ),
        (
            taxpayer_edit_POST_factory(
                eb_entity="1",
                cuit="20-3123214-1",
            ),
            ["cuit", "business_name"],
            ["20-3123214-1", "EB ARG"]
        ),
        (
            taxpayer_edit_POST_factory(
                eb_entity="1",
                payment_term=1,
            ),
            ["payment_term"],
            [30]
        )
    ])
    def test_form_valid_method_should_update_taxpayer_info(
        self,
        taxpayer_post_update,
        fields_changed,
        value_expected
    ):
        before_update = len(TaxPayer.objects.all())

        TAXPAYER_POST_UPDATE = taxpayer_post_update
        QUERY_FORM_TAXPAYER_POST_UPDATE = QueryDict('', mutable=True)
        QUERY_FORM_TAXPAYER_POST_UPDATE.update(
            TAXPAYER_POST_UPDATE
        )

        self.client.post(
            reverse(
                self.taxpayer_edit_url,
                kwargs=self.kwargs
            ),
            data=QUERY_FORM_TAXPAYER_POST_UPDATE
        )

        form_taxpayer = TaxPayerEditForm(data=QUERY_FORM_TAXPAYER_POST_UPDATE)
        self.assertTrue(form_taxpayer.is_valid())

        after_update = len(TaxPayer.objects.all())

        taxpayer = TaxPayerArgentina.objects.get(pk=self.taxpayer_id)

        self.assertEqual(before_update, after_update)

        for index, attribute in enumerate(fields_changed):
            self.assertEqual(
                getattr(taxpayer, attribute), value_expected[index]
            )

    def test_post_edit_active_taxpayer_as_supplier_changes_state_to_pending(self):
        status_approved = TAXPAYER_STATUS['Approved'].value
        status_pending = TAXPAYER_STATUS['Pending'].value
        self.taxpayer.taxpayer_state = status_approved
        self.client2.post(
            reverse(
                self.taxpayer_edit_url,
                kwargs=self.kwargs
            ),
            data=self.TAXPAYER_POST
        )
        edited_taxpayer_state = TaxPayer.objects.get(pk=self.taxpayer.id).taxpayer_state
        self.assertEqual(
            edited_taxpayer_state,
            status_pending,
        )

    def test_post_edit_active_taxpayer_as_ap_dont_chang_state(self):
        status_approved = TAXPAYER_STATUS['Approved'].value
        self.taxpayer.taxpayer_state = status_approved
        self.taxpayer.save()
        self.client.post(
            reverse(
                self.taxpayer_edit_url,
                kwargs=self.kwargs
            ),
            data=self.TAXPAYER_POST
        )
        edited_taxpayer_state = TaxPayer.objects.get(pk=self.taxpayer.id).taxpayer_state
        self.assertEqual(
            edited_taxpayer_state,
            status_approved
        )


class TestEditAddressInfo(TestCase):
    def setUp(self):
        self.client = Client()

        self.ap_group = Group.objects.get(name="ap_admin")
        self.ap_user = UserFactory(email='ap@eventbrite.com')
        self.ap_user.groups.add(self.ap_group)

        self.supplier_group = Group.objects.get(name="supplier")
        self.supplier_user = UserFactory(email='nahuelSupplier@gmail.com')
        self.supplier_user.groups.add(self.supplier_group)

        self.taxpayer = TaxPayerArgentinaFactory()
        self.taxpayer.taxpayer_state = TAXPAYER_STATUS['Approved'].value
        self.taxpayer.save()
        self.address = AddressFactory(taxpayer=self.taxpayer)

        self.address_edit_url = 'address-update'
        self.taxpayer_detail_url = 'supplier-details'
        self.ADDRESS_POST = {
            'address_form-street': 'San Martin',
            'address_form-number': '21312',
            'address_form-zip_code': '123',
            'address_form-city': 'Mendoza',
            'address_form-state': 'Mendoza',
            'address_form-country': 'AR',
        }
        self.kwargs = {
            'taxpayer_id': self.taxpayer.id,
            'address_id': self.address.id,
        }
        self.kwargs_taxpayer_id = {
            'taxpayer_id': self.taxpayer.id,
        }

    def _make_address_post(self):
        return self.client.post(
            reverse(
                self.address_edit_url,
                kwargs=self.kwargs
            ),
            data=self.ADDRESS_POST
        )

    def test_get_edit_address_view_as_ap(self):
        self.client.force_login(self.ap_user)
        response = self.client.get(
            reverse(
                self.address_edit_url,
                kwargs=self.kwargs
            )
        )
        self.assertEqual(
            'AP_app/edit-address-information.html',
            response.template_name[0]
        )

    def test_post_edit_address_info_as_ap_redirects_to_taxpayer_details(self):
        self.client.force_login(self.ap_user)
        response = self._make_address_post()

        # checking response status code and url should go to taxpayer detail
        self.assertEqual(HTTPStatus.FOUND, response.status_code)
        self.assertEqual(
            reverse(
                self.taxpayer_detail_url,
                kwargs=self.kwargs_taxpayer_id,
            ),
            response.url
        )

    def test_post_edit_address_info_as_ap_dont_change_status(self):
        self.client.force_login(self.ap_user)
        status_approved = TAXPAYER_STATUS['Approved'].value
        self._make_address_post()
        self.assertEqual(
            status_approved,
            TaxPayer.objects.get(pk=self.taxpayer.id).taxpayer_state
        )

    def test_post_edit_address_info_as_supplier_redirects_to_taxpayer_details(self):
        self.client.force_login(self.supplier_user)

        CompanyUserPermissionFactory(
            user=self.supplier_user,
            company=self.taxpayer.company
        )

        response = self._make_address_post()
        self.assertEqual(HTTPStatus.FOUND, response.status_code)
        self.assertEqual(
            reverse(
                self.taxpayer_detail_url,
                kwargs=self.kwargs_taxpayer_id,
            ),
            response.url
        )

    def test_post_edit_addres_info_as_supplier_change_status_to_pending(self):
        self.client.force_login(self.supplier_user)
        status_pending = TAXPAYER_STATUS['Pending'].value

        CompanyUserPermissionFactory(
            user=self.supplier_user,
            company=self.taxpayer.company
        )
        self._make_address_post()
        self.assertEqual(
            status_pending,
            TaxPayer.objects.get(pk=self.taxpayer.id).taxpayer_state
        )


class TestEditBankAccountInfo(TestCase):
    def setUp(self):
        self.client = Client()

        self.ap_group = Group.objects.get(name="ap_admin")
        self.ap_user = UserFactory(email='ap@eventbrite.com')
        self.ap_user.groups.add(self.ap_group)

        self.supplier_group = Group.objects.get(name="supplier")
        self.supplier_user = UserFactory(email='nahuelSupplier@gmail.com')
        self.supplier_user.groups.add(self.supplier_group)

        self.taxpayer = TaxPayerArgentinaFactory()
        self.taxpayer.taxpayer_state = TAXPAYER_STATUS['Approved'].value
        self.taxpayer.save()
        self.bank_account = BankAccountFactory(taxpayer=self.taxpayer)

        self.bank_update_url = 'bank-account-update'

        self.BANK_ACCOUNT_POST = {
            'bank_info': get_bank_info_example("CITIBANK N.A."),
            'bank_account_number': '123214',
        }

        self.taxpayer_detail_url = 'supplier-details'
        self.kwargs = {
            'taxpayer_id': self.taxpayer.id,
            'bank_id': self.bank_account.id,
        }
        self.kwargs_taxpayer_id = {
            'taxpayer_id': self.taxpayer.id,
        }

    def _make_bank_post(self):
        return self.client.post(
            reverse(
                self.bank_update_url,
                kwargs=self.kwargs
            ),
            data=self.BANK_ACCOUNT_POST
        )

    def test_get_bank_account_edit_view_as_ap(self):
        self.client.force_login(self.ap_user)
        response = self.client.get(
            reverse(self.bank_update_url, kwargs=self.kwargs)
        )

        self.assertEqual(
            HTTPStatus.OK,
            response.status_code
        )
        self.assertEqual(
            'AP_app/edit-bank-account-information.html',
            response.template_name[0]
        )

    def test_post_edit_bank_account_info_as_ap(self):
        self.client.force_login(self.ap_user)
        response = self._make_bank_post()
        self.assertEqual(HTTPStatus.FOUND, response.status_code)
        self.assertEqual(
            reverse(
                self.taxpayer_detail_url,
                kwargs=self.kwargs_taxpayer_id
            ),
            response.url
        )

    def test_post_edit_bank_account_info_as_ap_dont_change_status(self):
        self.client.force_login(self.ap_user)
        status_approved = TAXPAYER_STATUS['Approved'].value
        self._make_bank_post()
        self.assertEqual(
            status_approved,
            TaxPayer.objects.get(pk=self.taxpayer.id).taxpayer_state
        )

    def test_post_edit_bank_account_info_as_supplier_redirect_to_taxpayer_details(self):
        CompanyUserPermissionFactory(
            user=self.supplier_user,
            company=self.taxpayer.company
        )

        self.client.force_login(self.supplier_user)

        response = self._make_bank_post()
        self.assertEqual(HTTPStatus.FOUND, response.status_code)
        self.assertEqual(
            reverse(
                self.taxpayer_detail_url,
                kwargs=self.kwargs_taxpayer_id
            ),
            response.url
        )

    def test_post_edit_bank_info_as_supplier_change_status_to_pending(self):
        self.client.force_login(self.supplier_user)
        status_pending = TAXPAYER_STATUS['Pending'].value
        CompanyUserPermissionFactory(
            user=self.supplier_user,
            company=self.taxpayer.company
        )
        self._make_bank_post()
        self.assertEqual(
            status_pending,
            TaxPayer.objects.get(pk=self.taxpayer.id).taxpayer_state
        )


class TestCompanyCreateView(TestCase):
    def setUp(self):
        self.company_constants = {
            'name': 'Eventbrite',
            'description':
                'Bringing the world together through live experiences',
        }
        self.client = Client()

        self.ap_user = User.objects.create_user(email='ap@eventbrite.com')
        self.ap_user.groups.add(Group.objects.get(name='ap_admin'))
        self.user_with_social_evb1 = UserFactory(email='nahuel')
        self.user_with_social_evb1.groups.add(Group.objects.get(name='supplier'))

    def _make_post(self):
        self.client.force_login(self.ap_user)
        return self.client.post(
            reverse('company-create'),
            self.company_constants,
            follow=True,
        )

    def test_get_template_as_ap(self):
        self.client.force_login(self.ap_user)
        response = self.client.get('/suppliersite/ap/company/create')
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual(
            'AP_app/company_creation.html',
            response.template_name[0]
        )

    def test_get_template_as_supplier_redirects_to_supplier_home(self):
        self.client.force_login(self.ap_user)
        response = self.client.get(reverse('company-create'))
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual(
            'AP_app/company_creation.html',
            response.template_name[0]
        )

    def test_valid_company_creation(self):
        self.client.force_login(self.ap_user)
        self._make_post()
        self.assertEqual(
            Company.objects.last().name,
            self.company_constants['name']
        )

    def test_valid_redirection_after_company_creation(self):
        self.client.force_login(self.ap_user)
        response = self._make_post()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response.redirect_chain[0],
            (reverse('ap-taxpayers'), HTTPStatus.FOUND)
        )


class TestCompanyListView(TestCase):
    def setUp(self):
        self.company_list = [
            CompanyFactory(),
            CompanyFactory(),
            CompanyFactory(),
        ]
        self.client = Client()
        self.user = UserFactory()
        self.client.force_login(self.user)

    def test_company_list(self):
        response = self.client.get(reverse('company-list'))
        company1 = response.context[0]['company_list'][0]
        self.assertIn(company1, self.company_list)
        self.assertTrue(
            len(response.context[0]['company_list']) >= 3
        )

    def test_company_list_template(self):
        response = self.client.get(reverse('company-list'))
        self.assertTemplateUsed(response, 'supplier_app/company_list.html')


class TestCompanyInvite(TestCase):
    def setUp(self):
        CompanyFactory()
        self.client = Client()

    def _make_post(self, language='en'):
        response = self.client.post(
            path=reverse('company-invite'),
            data={
                'email': 'something@eventbrite.com',
                'company_id': '1',
                'language': language,
            },
        )
        return response

    def test_company_invite_sends_email_notification_in_spanish(self,):
        self._make_post("es")
        self.assertIn("Bienvenido a BriteSu!\nPor favor accede al siguiente link.", mail.outbox[0].body)
        self.assertIn("¡Gracias!", mail.outbox[0].body)

    def test_company_invite_sends_email_notification(self):
        self._make_post()
        self.assertEqual(
            mail.outbox[0].subject,
            email_notifications['company_invitation']['subject'],
        )

    @patch(
        'supplier_app.models.CompanyUniqueToken._token_generator',
        return_value=TOKEN_COMPANY
    )
    def test_company_invite_sends_token_in_body_and_is_persisted(self, mocked_token):
        self._make_post()
        self.assertIn(
            mocked_token.return_value,
            mail.outbox[0].alternatives[0][0],
        )
        self.assertEqual(
            CompanyUniqueToken.objects.last().token,
            TOKEN_COMPANY
        )

    def test_company_invite_redirect_to_companies_upon_email_invitation(self):
        response = self._make_post()
        self.assertEqual(
            response.url,
            reverse_lazy('company-list')
        )


class TestCompanyJoinView(TestCase):
    def setUp(self):
        self.client = Client()
        self.supplier_group = Group.objects.get(name='supplier')
        self.user = UserFactory()
        self.user.groups.add(self.supplier_group)
        self.url_company_select = 'company-selection'
        self.url_company_join = 'company-join'
        self.client.force_login(self.user)

    def _get_company_join_response(self, token=None):

        company_unique_token = CompanyUniqueTokenFactory() if not token else None
        kwargs = {'token': token or company_unique_token.token}
        return self.client.post(
            reverse(
                self.url_company_join,
                kwargs=kwargs
            ),
            follow=True,
        )

    def test_valid_token(self):

        response = self._get_company_join_response()
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK
        )
        self.assertEqual(
            response.template_name,
            ['supplier_app/supplier-home.html']
        )

    @patch(
        'supplier_app.models.CompanyUniqueToken._get_token_expiration_time',
        return_value=1*60
    )
    def test_invalid_token_is_expired(self, mocked_token_expiration_time):
        minutes = 2*60
        with freeze_time(timezone.now() - timedelta(minutes=minutes)):
            company_unique_token = CompanyUniqueTokenFactory()
        response = self._get_company_join_response(company_unique_token.token)
        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND
        )

    def test_wrong_token_should_redirect_404(self):
        CompanyUniqueTokenFactory()
        response = self._get_company_join_response('a230da6197be4436a4b686460289085c14a859d634a9daca2d7d137b178b193a')
        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND
        )

    @patch(
        'supplier_app.views.CompanyUserPermission.objects.create',
        side_effect=DatabaseError
    )
    def test_database_error_on_join_company_should_redirect_to_home_with_error_msg(self, db_error):
        company_unique_token = CompanyUniqueTokenFactory()
        response = self._get_company_join_response(company_unique_token.token)
        self.assertIn('supplier_app/supplier-home.html', response.template_name)
        self.assertContains(response, JOIN_COMPANY_ERROR_MESSAGE)

    def test_join_is_invalid_once_toke_is_used_by_user(self):
        company_unique_token = CompanyUniqueTokenFactory()
        self._get_company_join_response(company_unique_token.token)
        response = self._get_company_join_response(company_unique_token.token)
        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND
        )

    def test_logged_in_supplier_can_join_a_company(self):
        company_unique_token = CompanyUniqueTokenFactory()
        response = self._get_company_join_response(company_unique_token.token)
        self.assertIn(
            'supplier_app/supplier-home.html',
            response.template_name,
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK
        )
        self.assertTrue(
            self.user.groups.filter(name='supplier').exists()
        )

    def test_not_logged_in_supplier_cant_join_a_company(self):
        client = Client()
        supplier_user = UserFactory()
        supplier_user.groups.add(self.supplier_group)

        response = client.get(
            reverse('taxpayer-create'),
            follow=True
        )
        self.assertIn(
            'registration/login.html',
            response.template_name,
        )
        self.assertNotIn(
            'supplier_app/taxpayer-create.html',
            response.template_name
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK
        )
        self.assertTrue(
            supplier_user.groups.filter(name='supplier').exists()
        )

    def test_users_without_required_permission_cant_join_a_company(self):
        client = Client()
        user_without_supplier_permission = UserFactory(email='ap@eventbrite.com')
        ap_group = Group.objects.get(name='ap_admin')
        user_without_supplier_permission.groups.add(ap_group)

        client.force_login(user_without_supplier_permission)
        response = client.get(
            reverse('taxpayer-create'),
            follow=True,
        )
        self.assertIn(
            'AP_app/ap-taxpayers.html',
            response.template_name,
        )
        self.assertNotIn(
            'supplier_app/taxpayer-creat.html',
            response.template_name
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK
        )
        self.assertFalse(
            user_without_supplier_permission.groups.filter(name='supplier').exists()
        )


class TestCompanyJoin(TestCase):
    def setUp(self):
        self.client = Client()
        self.supplier_group = Group.objects.get(name="supplier")
        self.user = UserFactory()
        self.user.groups.add(self.supplier_group)
        self.client.force_login(self.user)
        self.url_company_join = 'company-join'

    def test_user_has_company_once_he_access_to_the_page_by_mail(self):
        company_unique_token = CompanyUniqueTokenFactory()
        kwargs = {'token': company_unique_token.token}
        response = self.client.post(
            reverse(
                self.url_company_join,
                kwargs=kwargs
            )
        )
        self.assertEqual(
            CompanyUserPermission.objects.last().user,
            self.user
        )
        self.assertEqual(
            CompanyUserPermission.objects.last().company,
            company_unique_token.company
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.FOUND
        )
        self.assertEqual(
            response.url,
            '/suppliersite/supplier'
        )

    def test_compnay_unique_token_is_deleted_once_user_joins_company(self):
        company_unique_token = CompanyUniqueTokenFactory()
        kwargs = {'token': company_unique_token.token}
        self.client.post(
            reverse(
                self.url_company_join,
                kwargs=kwargs
            )
        )
        with self.assertRaises(CompanyUniqueToken.DoesNotExist):
            CompanyUniqueToken.objects.get(token=company_unique_token.token)


class TestApprovalRefuse(TestCase):
    def setUp(self):
        self.taxpayer = TaxPayerArgentinaFactory()
        self.client = Client()

        self.ap_user = User.objects.create_user(email='ap@eventbrite.com')
        self.ap_user.groups.add(Group.objects.get(name='ap_admin'))
        self.user_with_social_evb1 = UserFactory(email='nahuel')
        self.user_with_social_evb1.groups.add(Group.objects.get(name='supplier'))
        self.client.force_login(self.ap_user)
        self.app_home_url = 'ap-taxpayers'
        self.supplier_home_url = 'supplier-home'
        self.handle_taxpayer_status_url = 'handle-taxpayer-status'
        self.kwargs = {
            'taxpayer_id': self.taxpayer.id
        }

    def _handle_taxpayer_status_request(self, action, follow=False):

        return self.client.post(
            reverse(
                self.handle_taxpayer_status_url,
                kwargs=self.kwargs
            ),
            {
                "action": action,
            },
            follow=follow,
        )

    def test_redirect_to_ap_home_when_approve_a_supplier(self):
        response = self._handle_taxpayer_status_request("approve")

        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            response.url,
            reverse(self.app_home_url)
            )

    def test_redirect_to_supplier_home_when_supplier_tries_to_approve_a_supplier(self):
        self.client.force_login(self.user_with_social_evb1)
        response = self._handle_taxpayer_status_request("approve")
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_change_taxpayer_status_to_active_when_clicking_aprove_button(self):
        self._handle_taxpayer_status_request("approve")
        self.assertEqual(
            TaxPayer.objects.get(pk=self.taxpayer.id).taxpayer_state,
            'APPROVED'
        )

    def test_change_taxpayer_status_to_active_sends_email_notification(self):
        CompanyUserPermissionFactory(
            user=UserFactory(),
            company=self.taxpayer.company
        )
        self._handle_taxpayer_status_request("approve")
        self.assertEqual(
            mail.outbox[0].subject,
            email_notifications['taxpayer_approval']['subject']
        )

        self.assertIn(
            settings.SUPPLIER_HOME_URL,
            mail.outbox[0].alternatives[0][0]
        )

    def test_redirect_to_ap_home_when_deny_a_supplier(self):
        response = self._handle_taxpayer_status_request("deny")

        self.assertEqual(response.status_code, 302)

        self.assertEqual(response.url, '/suppliersite/ap')

    @patch(
        'supplier_app.change_status_strategy.StrategyApprove.send_email',
        side_effect=CouldNotSendEmailError
    )
    def test_error_sending_mail_should_display_error_msg_in_taxpayer_approval(self, send_mail_mocked):
        response = self._handle_taxpayer_status_request("approve", True)
        self.assertContains(response, EMAIL_ERROR_MESSAGE)

    @patch(
        'supplier_app.change_status_strategy.StrategyDeny.send_email',
        side_effect=CouldNotSendEmailError
    )
    def test_error_sending_mail_should_display_error_msg_in_taxpayer_denial(self, send_mail_mocked):
        response = self._handle_taxpayer_status_request("deny", True)
        self.assertContains(response, EMAIL_ERROR_MESSAGE)

    @patch(
        'supplier_app.views.TaxPayer.objects.get',
        side_effect=ObjectDoesNotExist
    )
    def test_nonexistent_taxpayer_should_display_error_message_on_approve(self, send_mail_mocked):
        response = self._handle_taxpayer_status_request("approve", True)
        self.assertContains(response, TAXPAYER_NOT_EXISTS_MESSAGE.encode('utf-8'))

    @patch(
        'supplier_app.views.TaxPayer.objects.get',
        side_effect=ObjectDoesNotExist
    )
    def test_nonexistent_taxpayer_should_display_error_message_on_denial(self, send_mail_mocked):
        response = self._handle_taxpayer_status_request("deny", True)
        self.assertContains(response, TAXPAYER_NOT_EXISTS_MESSAGE.encode('utf-8'))

    def test_redirect_to_supplier_home_when_supplier_tries_to_deny_a_supplier(self):
        self.client.force_login(self.user_with_social_evb1)
        response = self._handle_taxpayer_status_request("deny")
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_change_taxpayer_status_to_DENIED_when_clicking_deny_button(self):
        self._handle_taxpayer_status_request("deny")

        self.assertEqual(
            TaxPayer.objects.get(pk=self.taxpayer.id).taxpayer_state,
            'DENIED'
        )

    def test_change_taxpayer_status_to_denied_sends_email_notification(self):
        CompanyUserPermissionFactory(
            user=UserFactory(),
            company=self.taxpayer.company
        )
        self._handle_taxpayer_status_request("deny")

        self.assertEqual(
            mail.outbox[0].subject,
            email_notifications['taxpayer_denial']['subject']
        )

        self.assertIn(
            settings.SUPPLIER_HOME_URL,
            mail.outbox[0].alternatives[0][0]
        )


class TestNotifyMessages(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.supplier_group = Group.objects.get(name='supplier')
        self.supplier_user = UserFactory()
        self.supplier_user.groups.add(self.supplier_group)
        self.supplier_without_company = UserFactory()
        self.supplier_without_company.groups.add(self.supplier_group)
        CompanyUserPermissionFactory(user=self.supplier_user)
        self.client.force_login(self.supplier_user)
        self.taxpayer_creation_url = 'taxpayer-create'
        self.email_invitation_url = 'company-invite'
        self.supplier_home_url = 'supplier-home'
        self.company_constants = {
            'email': 'something@eventbrite.com',
            'company_id': '1',
            'language': 'en',
        }
        self.eb_entity = EBEntityFactory()
        self.POST = taxpayer_creation_POST_factory(self.eb_entity.id)

    def _make_email_invitation_post(self):
        return self.client.post(
            reverse(self.email_invitation_url),
            self.company_constants,
            follow=True
        )

    @patch(
        'supplier_app.models.CompanyUniqueToken._token_generator',
        return_value=TOKEN_COMPANY
    )
    def test_send_mail_correctly_should_show_success_message(self, token_mocked):
        response = self._make_email_invitation_post()
        self.assertContains(response, EMAIL_SUCCESS_MESSAGE)

    def test_supplier_without_company_should_see_notification_message_in_home(self):
        self.client.force_login(self.supplier_without_company)
        response = self.client.get(
            reverse(self.supplier_home_url),
        )
        self.assertContains(response, COMPANY_ERROR_MESSAGE)

    def test_supplier_without_company_cant_create_a_taxpayer_message(self):
        self.client.force_login(self.supplier_without_company)
        response = self.client.post(
            reverse(self.taxpayer_creation_url),
            self.POST,
            follow=True,
        )
        self.assertContains(response, TAXPAYER_CREATION_ERROR_MESSAGE)

    def test_taxpayer_creation_success_should_display_success_message(self):
        self.client.force_login(self.supplier_user)
        response = self.client.post(
            reverse(self.taxpayer_creation_url),
            self.POST,
            follow=True
        )
        self.assertContains(response, TAXPAYER_CREATION_SUCCESS_MESSAGE)

    def test_taxpayer_creation_error_should_display_error_message(self):
        response = self.client.post(
            reverse(self.taxpayer_creation_url),
            {
                'asd': 'asd',
            },
            follow=True,
        )
        self.assertContains(response, TAXPAYER_FORM_INVALID_MESSAGE)


class TestTaxpayerHistory(TestCase):
    def setUp(self):
        self.client = Client()
        self.ap_user = ApUserFactory()
        self.ap_group = Group.objects.get(name="ap_admin")
        self.ap_user.groups.add(self.ap_group)
        self.client.force_login(self.ap_user)

        self.taxpayer = TaxPayerArgentinaFactory(business_name="SupraSA")

    def test_create_new_row_in_history_taxpayer_table(self):
        kwargs = {
            'taxpayer_id': self.taxpayer.id,
        }

        TAXPAYER_POST = QueryDict("", mutable=True)
        TAXPAYER_POST.update(
            taxpayer_edit_POST_factory(eb_entity=EBEntityFactory().id)
        )

        row_before_modification = len(self.taxpayer.history.all())

        self.client.post(
            reverse(
                'taxpayer-update',
                kwargs=kwargs
            ),
            data=TAXPAYER_POST,
        )

        row_after_modification = len(self.taxpayer.history.all())

        last_row_taxpayer_history = self.taxpayer.history.latest()
        updated_taxpayer = TaxPayerArgentina.objects.get(pk=self.taxpayer.id)

        self.assertGreater(row_after_modification, row_before_modification)

        self.assertEqual(updated_taxpayer.cuit, last_row_taxpayer_history.cuit)
        self.assertEqual(updated_taxpayer.payment_term, last_row_taxpayer_history.payment_term)
        self.assertEqual(updated_taxpayer.payment_type, last_row_taxpayer_history.payment_type)
        self.assertEqual(updated_taxpayer.workday_id, last_row_taxpayer_history.workday_id)
        self.assertEqual(updated_taxpayer.business_name, last_row_taxpayer_history.business_name)
        self.assertEqual(updated_taxpayer.taxpayer_state, last_row_taxpayer_history.taxpayer_state)
        self.assertEqual(updated_taxpayer.country, last_row_taxpayer_history.country)
        self.assertEqual(updated_taxpayer.taxpayer_comments, last_row_taxpayer_history.taxpayer_comments)

    def test_create_new_row_in_history_address_table(self):
        address = AddressFactory(taxpayer=self.taxpayer)
        kwargs = {
            'taxpayer_id': self.taxpayer.id,
            'address_id': address.id,
        }

        ADDRESS_POST = {
            'address_form-street': 'San Martin',
            'address_form-number': '21312',
            'address_form-zip_code': '123',
            'address_form-city': 'Mendoza',
            'address_form-state': 'Mendoza',
            'address_form-country': 'AR',
        }

        row_before_modification = len(address.history.all())

        self.client.post(
            reverse(
                'address-update',
                kwargs=kwargs
            ),
            data=ADDRESS_POST
        )

        row_after_modification = len(address.history.all())

        last_row_address_history = address.history.latest()
        updated_address = Address.objects.get(pk=address.id)

        self.assertGreater(row_after_modification, row_before_modification)

        self.assertEqual(updated_address.street, last_row_address_history.street)
        self.assertEqual(updated_address.number, last_row_address_history.number)
        self.assertEqual(updated_address.zip_code, last_row_address_history.zip_code)
        self.assertEqual(updated_address.city, last_row_address_history.city)
        self.assertEqual(updated_address.state, last_row_address_history.state)
        self.assertEqual(updated_address.country, last_row_address_history.country)

    def test_create_new_row_in_history_bank_account_table(self):
        bank_account = BankAccountFactory(taxpayer=self.taxpayer)
        kwargs = {
            'taxpayer_id': self.taxpayer.id,
            'bank_id': bank_account.id,
        }

        BANK_ACCOUNT_POST = {
            'bank_info': get_bank_info_example("CITIBANK N.A."),
            'bank_account_number': '123214',
        }

        row_before_modification = len(bank_account.history.all())

        self.client.post(
            reverse(
                'bank-account-update',
                kwargs=kwargs
            ),
            data=BANK_ACCOUNT_POST
        )

        row_after_modification = len(bank_account.history.all())

        last_row_bank_account_history = bank_account.history.latest()
        updated_bank = BankAccount.objects.get(pk=bank_account.id)

        self.assertGreater(row_after_modification, row_before_modification)

        self.assertEqual(updated_bank.bank_account_number, last_row_bank_account_history.bank_account_number)
        self.assertEqual(updated_bank.bank_info, last_row_bank_account_history.bank_info)

    def test_history_taxpayer_should_contain_old_and_new_values(self):
        old_name = self.taxpayer.business_name
        self.taxpayer.business_name = "New_SupraSA"
        new_name = self.taxpayer.business_name
        self.taxpayer.save()

        response = self.client.get(
            reverse(
                'taxpayer-history',
                kwargs={'pk': self.taxpayer.id}
                ),
        )
        self.assertContains(response, old_name)
        self.assertContains(response, new_name)

        # last: means last in the table, so it is old data
        self.assertEqual(old_name, self.taxpayer.history.last().business_name)
        # latest: means that is updated data
        self.assertEqual(new_name, self.taxpayer.history.latest().business_name)
        self.assertEqual(response.template_name[0], 'AP_app/taxpayer-history-list.html')

    def test_history_address_should_contain_old_and_new_values(self):
        address = AddressFactory(taxpayer=self.taxpayer)

        old_street = address.street
        address.street = "New Street"
        new_street = address.street

        address.save()

        response = self.client.get(
            reverse(
                'taxpayer-history',
                kwargs={'pk': address.taxpayer.id}
                ),
        )

        self.assertContains(response, old_street)
        self.assertContains(response, new_street)

        # last: means last in the table, so it is old data
        self.assertEqual(old_street, address.history.last().street)
        # latest: means that is updated data
        self.assertEqual(new_street, address.history.latest().street)
        self.assertEqual(response.template_name[0], 'AP_app/taxpayer-history-list.html')

    def test_history_bank_account_should_contain_old_and_new_values(self):
        bank_account = BankAccountFactory(
            taxpayer=self.taxpayer,
            bank_account_number="132456789",
        )

        old_bank_account_number = bank_account.bank_account_number
        bank_account.bank_account_number = "17508976543"
        new_bank_account_number = bank_account.bank_account_number

        bank_account.save()

        response = self.client.get(
            reverse(
                'taxpayer-history',
                kwargs={'pk': bank_account.taxpayer.id}
                ),
        )

        self.assertContains(response, old_bank_account_number)
        self.assertContains(response, new_bank_account_number)

        # last: means last in the table, so it is old data
        self.assertEqual(old_bank_account_number, bank_account.history.last().bank_account_number)
        # latest: means that is updated data
        self.assertEqual(new_bank_account_number, bank_account.history.latest().bank_account_number)
        self.assertEqual(response.template_name[0], 'AP_app/taxpayer-history-list.html')


class TestTaxpayerCommentView(TestCase):
    def setUp(self):
        self.client = Client()

        self.ap_group = Group.objects.get(name="ap_admin")
        self.ap_user = UserFactory(email='ap@eventbrite.com')
        self.ap_user.groups.add(self.ap_group)

        self.supplier_group = Group.objects.get(name="supplier")
        self.supplier_user = UserFactory(email='nahuelSupplier@gmail.com')
        self.supplier_user.groups.add(self.supplier_group)

        self.supplier_detail_url = 'supplier-details'
        self.comment_post_url = 'taxpayer-comment'

        self.file_mock = MagicMock(spec=File)
        self.file_mock.name = 'test.pdf'
        self.file_mock.size = 50
        self.company = CompanyFactory(
            name='FakeCompany',
            description='Best catering worldwide'
        )
        self.companyuserpermission = CompanyUserPermissionFactory(
            company=self.company,
            user=self.supplier_user
        )
        self.taxpayer_example = TaxPayerArgentinaFactory(
            afip_registration_file=self.file_mock,
            witholding_taxes_file=self.file_mock,
            company=self.company,
        )
        BankAccountFactory(
            taxpayer=self.taxpayer_example,
            bank_cbu_file=self.file_mock
            )
        AddressFactory(taxpayer=self.taxpayer_example)
        self.kwargs = {
            'taxpayer_id': self.taxpayer_example.id
        }
        self.comment_post = {
            'message': 'Testing comment',
            'user': self.supplier_user.id,
            'taxpayer': self.taxpayer_example.id
        }

    def _make_comment_post(self):
        return self.client.post(
            reverse(
                self.comment_post_url,
                kwargs=self.kwargs
            ),
            data=self.comment_post,
            follow=True
        )

    def test_request_change_btn_for_ap_in_comment_submit_form(self):
        self.client.force_login(self.ap_user)
        response = self.client.get(
            reverse(
                self.supplier_detail_url,
                kwargs=self.kwargs
            ),
        )
        self.assertContains(response, 'Request Change')

    def test_make_comment_btn_for_supplier_in_comment_submit_form(self):
        self.client.force_login(self.supplier_user)
        response = self.client.get(
            reverse(
                self.supplier_detail_url,
                kwargs=self.kwargs
            ),
        )
        self.assertContains(response, 'Make Comment')

    def test_supplier_make_comment(self):
        self.client.force_login(self.supplier_user)
        self._make_comment_post()
        self.assertEqual(
            TaxpayerComment.objects.last().message,
            self.comment_post['message']
        )

    def test_supplier_without_taxpayer_ownership_cant_make_comment(self):

        user = UserFactory(email='supplier@gmail.com')
        user.groups.add(self.supplier_group)

        self.client.force_login(user)
        response = self._make_comment_post()
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)

    def test_ap_make_comment(self):
        self.client.force_login(self.ap_user)
        self._make_comment_post()
        # comment persist
        self.assertEqual(
            TaxpayerComment.objects.last().message,
            self.comment_post['message']
        )
        # taxpayer state changes to change required
        self.assertEqual(
            TaxPayer.objects.get(pk=self.taxpayer_example.id).taxpayer_state,
            TAXPAYER_STATUS['Change required'].value
        )
