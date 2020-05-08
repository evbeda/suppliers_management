# -*- coding: utf-8 -*-
# Generated by Django 1.11.24 on 2019-11-11 20:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supplier_app', '0014_auto_20191106_1457'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='taxpayercomment',
            options={'ordering': ['-comment_date_received']},
        ),
        migrations.AlterField(
            model_name='bankaccount',
            name='bank_info',
            field=models.IntegerField(choices=[(7, 'BANCO DE GALICIA Y BUENOS AIRES S.A.U.'), (11, 'BANCO DE LA NACION ARGENTINA'), (14, 'BANCO DE LA PROVINCIA DE BUENOS AIRES'), (15, 'INDUSTRIAL AND COMMERCIAL BANK OF CHINA'), (16, 'CITIBANK N.A.'), (17, 'BBVA BANCO FRANCES S.A.'), (20, 'BANCO DE LA PROVINCIA DE CORDOBA S.A.'), (27, 'BANCO SUPERVIELLE S.A.'), (29, 'BANCO DE LA CIUDAD DE BUENOS AIRES'), (34, 'BANCO PATAGONIA S.A.'), (44, 'BANCO HIPOTECARIO S.A.'), (45, 'BANCO DE SAN JUAN S.A.'), (60, 'BANCO DEL TUCUMAN S.A.'), (65, 'BANCO MUNICIPAL DE ROSARIO'), (72, 'BANCO SANTANDER RIO S.A.'), (83, 'BANCO DEL CHUBUT S.A.'), (86, 'BANCO DE SANTA CRUZ S.A.'), (93, 'BANCO DE LA PAMPA SOCIEDAD DE ECONOMÍA M'), (94, 'BANCO DE CORRIENTES S.A.'), (97, 'BANCO PROVINCIA DEL NEUQUÉN SOCIEDAD ANÓNIMA'), (143, 'BRUBANK S.A.U.'), (147, 'BANCO INTERFINANZAS S.A.'), (150, 'HSBC BANK ARGENTINA S.A.'), (165, 'JPMORGAN CHASE BANK, NATIONAL ASSOCIATIO'), (191, 'BANCO CREDICOOP COOPERATIVO LIMITADO'), (198, 'BANCO DE VALORES S.A.'), (247, 'BANCO ROELA S.A.'), (254, 'BANCO MARIVA S.A.'), (259, 'BANCO ITAU ARGENTINA S.A.'), (262, 'BANK OF AMERICA, NATIONAL ASSOCIATION'), (266, 'BNP PARIBAS'), (268, 'BANCO PROVINCIA DE TIERRA DEL FUEGO'), (269, 'BANCO DE LA REPUBLICA ORIENTAL DEL URUGU'), (277, 'BANCO SAENZ S.A.'), (281, 'BANCO MERIDIAN S.A.'), (285, 'BANCO MACRO S.A.'), (299, 'BANCO COMAFI SOCIEDAD ANONIMA'), (300, 'BANCO DE INVERSION Y COMERCIO EXTERIOR S'), (301, 'BANCO PIANO S.A.'), (305, 'BANCO JULIO SOCIEDAD ANONIMA'), (309, 'BANCO RIOJA SOCIEDAD ANONIMA UNIPERSONAL'), (310, 'BANCO DEL SOL S.A.'), (311, 'NUEVO BANCO DEL CHACO S. A.'), (312, 'BANCO VOII S.A.'), (315, 'BANCO DE FORMOSA S.A.'), (319, 'BANCO CMF S.A.'), (321, 'BANCO DE SANTIAGO DEL ESTERO S.A.'), (322, 'BANCO INDUSTRIAL S.A.'), (330, 'NUEVO BANCO DE SANTA FE SOCIEDAD ANONIMA'), (331, 'BANCO CETELEM ARGENTINA S.A.'), (332, 'BANCO DE SERVICIOS FINANCIEROS S.A.'), (336, 'BANCO BRADESCO ARGENTINA S.A.U.'), (338, 'BANCO DE SERVICIOS Y TRANSACCIONES S.A.'), (339, 'RCI BANQUE S.A.'), (340, 'BACS BANCO DE CREDITO Y SECURITIZACION S'), (341, 'BANCO MASVENTAS S.A.'), (384, 'WILOBANK S.A.'), (386, 'NUEVO BANCO DE ENTRE RÍOS S.A.'), (389, 'BANCO COLUMBIA S.A.'), (426, 'BANCO BICA S.A.'), (431, 'BANCO COINAG S.A.'), (432, 'BANCO DE COMERCIO S.A.'), (44059, 'FORD CREDIT COMPAÑIA FINANCIERA S.A.'), (44077, 'COMPAÑIA FINANCIERA ARGENTINA S.A.'), (44088, 'VOLKSWAGEN FINANCIAL SERVICES COMPAÑIA F'), (44090, 'CORDIAL COMPAÑÍA FINANCIERA S.A.'), (44092, 'FCA COMPAÑIA FINANCIERA S.A.'), (44093, 'GPAT COMPAÑIA FINANCIERA S.A.U.'), (44094, 'MERCEDES-BENZ COMPAÑÍA FINANCIERA ARGENT'), (44095, 'ROMBO COMPAÑÍA FINANCIERA S.A.'), (44096, 'JOHN DEERE CREDIT COMPAÑÍA FINANCIERA S.'), (44098, 'PSA FINANCE ARGENTINA COMPAÑÍA FINANCIER'), (44099, 'TOYOTA COMPAÑÍA FINANCIERA DE ARGENTINA'), (44100, 'FINANDINO COMPAÑIA FINANCIERA S.A.'), (45056, 'MONTEMAR COMPAÑIA FINANCIERA S.A.'), (45072, 'TRANSATLANTICA COMPAÑIA FINANCIERA S.A.'), (65203, 'CREDITO REGIONAL COMPAÑIA FINANCIERA S.A')], verbose_name='Bank name'),
        ),
        migrations.AlterField(
            model_name='historicalbankaccount',
            name='bank_info',
            field=models.IntegerField(choices=[(7, 'BANCO DE GALICIA Y BUENOS AIRES S.A.U.'), (11, 'BANCO DE LA NACION ARGENTINA'), (14, 'BANCO DE LA PROVINCIA DE BUENOS AIRES'), (15, 'INDUSTRIAL AND COMMERCIAL BANK OF CHINA'), (16, 'CITIBANK N.A.'), (17, 'BBVA BANCO FRANCES S.A.'), (20, 'BANCO DE LA PROVINCIA DE CORDOBA S.A.'), (27, 'BANCO SUPERVIELLE S.A.'), (29, 'BANCO DE LA CIUDAD DE BUENOS AIRES'), (34, 'BANCO PATAGONIA S.A.'), (44, 'BANCO HIPOTECARIO S.A.'), (45, 'BANCO DE SAN JUAN S.A.'), (60, 'BANCO DEL TUCUMAN S.A.'), (65, 'BANCO MUNICIPAL DE ROSARIO'), (72, 'BANCO SANTANDER RIO S.A.'), (83, 'BANCO DEL CHUBUT S.A.'), (86, 'BANCO DE SANTA CRUZ S.A.'), (93, 'BANCO DE LA PAMPA SOCIEDAD DE ECONOMÍA M'), (94, 'BANCO DE CORRIENTES S.A.'), (97, 'BANCO PROVINCIA DEL NEUQUÉN SOCIEDAD ANÓNIMA'), (143, 'BRUBANK S.A.U.'), (147, 'BANCO INTERFINANZAS S.A.'), (150, 'HSBC BANK ARGENTINA S.A.'), (165, 'JPMORGAN CHASE BANK, NATIONAL ASSOCIATIO'), (191, 'BANCO CREDICOOP COOPERATIVO LIMITADO'), (198, 'BANCO DE VALORES S.A.'), (247, 'BANCO ROELA S.A.'), (254, 'BANCO MARIVA S.A.'), (259, 'BANCO ITAU ARGENTINA S.A.'), (262, 'BANK OF AMERICA, NATIONAL ASSOCIATION'), (266, 'BNP PARIBAS'), (268, 'BANCO PROVINCIA DE TIERRA DEL FUEGO'), (269, 'BANCO DE LA REPUBLICA ORIENTAL DEL URUGU'), (277, 'BANCO SAENZ S.A.'), (281, 'BANCO MERIDIAN S.A.'), (285, 'BANCO MACRO S.A.'), (299, 'BANCO COMAFI SOCIEDAD ANONIMA'), (300, 'BANCO DE INVERSION Y COMERCIO EXTERIOR S'), (301, 'BANCO PIANO S.A.'), (305, 'BANCO JULIO SOCIEDAD ANONIMA'), (309, 'BANCO RIOJA SOCIEDAD ANONIMA UNIPERSONAL'), (310, 'BANCO DEL SOL S.A.'), (311, 'NUEVO BANCO DEL CHACO S. A.'), (312, 'BANCO VOII S.A.'), (315, 'BANCO DE FORMOSA S.A.'), (319, 'BANCO CMF S.A.'), (321, 'BANCO DE SANTIAGO DEL ESTERO S.A.'), (322, 'BANCO INDUSTRIAL S.A.'), (330, 'NUEVO BANCO DE SANTA FE SOCIEDAD ANONIMA'), (331, 'BANCO CETELEM ARGENTINA S.A.'), (332, 'BANCO DE SERVICIOS FINANCIEROS S.A.'), (336, 'BANCO BRADESCO ARGENTINA S.A.U.'), (338, 'BANCO DE SERVICIOS Y TRANSACCIONES S.A.'), (339, 'RCI BANQUE S.A.'), (340, 'BACS BANCO DE CREDITO Y SECURITIZACION S'), (341, 'BANCO MASVENTAS S.A.'), (384, 'WILOBANK S.A.'), (386, 'NUEVO BANCO DE ENTRE RÍOS S.A.'), (389, 'BANCO COLUMBIA S.A.'), (426, 'BANCO BICA S.A.'), (431, 'BANCO COINAG S.A.'), (432, 'BANCO DE COMERCIO S.A.'), (44059, 'FORD CREDIT COMPAÑIA FINANCIERA S.A.'), (44077, 'COMPAÑIA FINANCIERA ARGENTINA S.A.'), (44088, 'VOLKSWAGEN FINANCIAL SERVICES COMPAÑIA F'), (44090, 'CORDIAL COMPAÑÍA FINANCIERA S.A.'), (44092, 'FCA COMPAÑIA FINANCIERA S.A.'), (44093, 'GPAT COMPAÑIA FINANCIERA S.A.U.'), (44094, 'MERCEDES-BENZ COMPAÑÍA FINANCIERA ARGENT'), (44095, 'ROMBO COMPAÑÍA FINANCIERA S.A.'), (44096, 'JOHN DEERE CREDIT COMPAÑÍA FINANCIERA S.'), (44098, 'PSA FINANCE ARGENTINA COMPAÑÍA FINANCIER'), (44099, 'TOYOTA COMPAÑÍA FINANCIERA DE ARGENTINA'), (44100, 'FINANDINO COMPAÑIA FINANCIERA S.A.'), (45056, 'MONTEMAR COMPAÑIA FINANCIERA S.A.'), (45072, 'TRANSATLANTICA COMPAÑIA FINANCIERA S.A.'), (65203, 'CREDITO REGIONAL COMPAÑIA FINANCIERA S.A')], verbose_name='Bank name'),
        ),
        migrations.AlterField(
            model_name='historicaltaxpayer',
            name='taxpayer_state',
            field=models.CharField(choices=[('APPROVED', 'Approved'), ('CHANGE REQUIRED', 'Change required'), ('PENDING', 'Pending'), ('DENIED', 'Denied'), ('CHANGES PENDING', 'Changes pending')], default='PENDING', max_length=200),
        ),
        migrations.AlterField(
            model_name='historicaltaxpayer',
            name='workday_id',
            field=models.CharField(db_index=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='historicaltaxpayerargentina',
            name='taxpayer_state',
            field=models.CharField(choices=[('APPROVED', 'Approved'), ('CHANGE REQUIRED', 'Change required'), ('PENDING', 'Pending'), ('DENIED', 'Denied'), ('CHANGES PENDING', 'Changes pending')], default='PENDING', max_length=200),
        ),
        migrations.AlterField(
            model_name='historicaltaxpayerargentina',
            name='workday_id',
            field=models.CharField(db_index=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='taxpayer',
            name='taxpayer_state',
            field=models.CharField(choices=[('APPROVED', 'Approved'), ('CHANGE REQUIRED', 'Change required'), ('PENDING', 'Pending'), ('DENIED', 'Denied'), ('CHANGES PENDING', 'Changes pending')], default='PENDING', max_length=200),
        ),
        migrations.AlterField(
            model_name='taxpayer',
            name='workday_id',
            field=models.CharField(max_length=200),
        ),
    ]
