import sys
import re
import os
import boto3
import io
from PIL import Image
import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz
from pdf2image import convert_from_path
import pytesseract
import json
import math
import cv2
import datetime

def read_image(Ima, structData):
    im = Image.open(Ima)
    buffered = io.BytesIO()
    im.save(buffered, format='PNG')

    AWS_S3_CREDS = {
        "aws_access_key_id": "AKIAYIOUTAHBQNFUWBUV",  # os.getenv("AWS_ACCESS_KEY")
        "aws_secret_access_key": "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"  # os.getenv("AWS_SECRET_KEY")
    }

    client = boto3.client('textract', **AWS_S3_CREDS, region_name='us-east-2')
    response = client.analyze_document(
        Document={'Bytes': buffered.getvalue()},
        FeatureTypes=['TABLES'])

    def map_blocks(blocks, block_type):
        return {
            block['Id']: block
            for block in blocks
            if block['BlockType'] == block_type
        }

    blocks = response['Blocks']
    tables = map_blocks(blocks, 'TABLE')
    cells = map_blocks(blocks, 'CELL')
    words = map_blocks(blocks, 'WORD')
    selections = map_blocks(blocks, 'SELECTION_ELEMENT')

    def get_children_ids(block):
        for rels in block.get('Relationships', []):
            if rels['Type'] == 'CHILD':
                yield from rels['Ids']

    dataframes = []

    for table in tables.values():

        # Determine all the cells that belong to this table
        table_cells = [cells[cell_id] for cell_id in get_children_ids(table)]

        # Determine the table's number of rows and columns
        n_rows = max(cell['RowIndex'] for cell in table_cells)
        n_cols = max(cell['ColumnIndex'] for cell in table_cells)
        content = [[None for _ in range(n_cols)] for _ in range(n_rows)]

        # Fill in each cell
        for cell in table_cells:
            cell_contents = [
                words[child_id]['Text']
                if child_id in words
                else selections[child_id]['SelectionStatus']
                for child_id in get_children_ids(cell)
            ]
            i = cell['RowIndex'] - 1
            j = cell['ColumnIndex'] - 1
            content[i][j] = ' '.join(cell_contents)

        # We assume that the first row corresponds to the column names
        dataframe = pd.DataFrame(content[1:], columns=content[0])
        dataframes.append(dataframe)
    this_data = None
    str1 = 'DESCRIPCIÓN'
    str2 = "Descrip. artículo"
    str3 = "Artículo/ Cod.cliente"
    str4 = 'DESCRIPCIÓN:'
    str5 = "CONCEPTO"
    str6 = "UDS"
    str7 = "Concepto"
    str8 = "Descripción"
    str9 = "DESCRIPCION"
    str10 = "Description articulo"
    str11 = "Description"
    str12 = "DESCRIPCIÓN ARTICULO"
    str13 = "Unidades Descripción"
    str14 = "PRODUCTO"
    str15 = "Articulo"
    str16 = 'Denominación /Referencia'
    str17 = 'DESCRIPCIÓN'
    str18 = 'REF.'
    str19 = "Codigo"
    str20 = "Lote"
    str21 = "MM Num. articulo"
    str22 = "MM Num. artículo"
    str23 = "Descripción Artículo"
    str24 = "CÓDIGO"
    str25 = "ARTÍCULO"
    str26 = "MM Num."
    zero = False
    one = False
    two = False
    three = False

    if str1 in dataframes[0].columns \
            or str2 in dataframes[0].columns \
            or str3 in dataframes[0].columns \
            or str4 in dataframes[0].columns or str5 in dataframes[0].columns or str6 in dataframes[0].columns \
            or str7 in dataframes[0].columns or str8 in dataframes[0].columns or str9 in dataframes[0].columns \
            or str10 in dataframes[0].columns or str11 in dataframes[0].columns or str12 in dataframes[0].columns \
            or str13 in dataframes[0].columns or str14 in dataframes[0].columns or str15 in dataframes[0].columns \
            or str16 in dataframes[0].columns or str17 in dataframes[0].columns or str18 in dataframes[0].columns \
            or str19 in dataframes[0].columns or str20 in dataframes[0].columns or str21 in dataframes[0].columns \
            or str22 in dataframes[0].columns or str23 in dataframes[0].columns or str24 in dataframes[0].columns \
            or str25 in dataframes[0].columns or str26 in dataframes[0].columns:
        this_data = pd.DataFrame(dataframes[0])
        zero = True

    elif len(dataframes) > 1 and (str1 in dataframes[1].columns \
                                  or str2 in dataframes[1].columns \
                                  or str3 in dataframes[1].columns \
                                  or str4 in dataframes[1].columns or str5 in dataframes[1].columns or str6 in
                                  dataframes[1].columns \
                                  or str7 in dataframes[1].columns or str8 in dataframes[1].columns or str9 in
                                  dataframes[1].columns \
                                  or str10 in dataframes[1].columns or str11 in dataframes[1].columns or str12 in
                                  dataframes[1].columns \
                                  or str13 in dataframes[1].columns or str14 in dataframes[1].columns or str15 in
                                  dataframes[1].columns \
                                  or str16 in dataframes[1].columns or str17 in dataframes[1].columns or str18 in
                                  dataframes[1].columns \
                                  or str19 in dataframes[1].columns or str20 in dataframes[1].columns or str21 in
                                  dataframes[1].columns \
                                  or str22 in dataframes[1].columns or str23 in dataframes[1].columns or str24 in
                                  dataframes[1].columns \
                                  or str25 in dataframes[1].columns or str26 in dataframes[1].columns):
        this_data = pd.DataFrame(dataframes[1])
        one = True

    elif len(dataframes) > 2 and (str1 in dataframes[2].columns \
                                  or str2 in dataframes[2].columns \
                                  or str3 in dataframes[2].columns \
                                  or str4 in dataframes[2].columns or str5 in dataframes[2].columns or str6 in
                                  dataframes[2].columns \
                                  or str7 in dataframes[2].columns or str8 in dataframes[2].columns or str9 in
                                  dataframes[2].columns \
                                  or str10 in dataframes[2].columns or str11 in dataframes[2].columns or str12 in
                                  dataframes[2].columns \
                                  or str13 in dataframes[2].columns or str14 in dataframes[2].columns or str15 in
                                  dataframes[2].columns \
                                  or str16 in dataframes[2].columns or str17 in dataframes[2].columns or str18 in
                                  dataframes[2].columns \
                                  or str19 in dataframes[2].columns or str20 in dataframes[2].columns or str21 in
                                  dataframes[2].columns \
                                  or str22 in dataframes[2].columns or str23 in dataframes[2].columns or str24 in
                                  dataframes[2].columns \
                                  or str25 in dataframes[2].columns or str26 in dataframes[2].columns):
        this_data = pd.DataFrame(dataframes[2])
        two = True

    elif len(dataframes) > 3 and (str1 in dataframes[3].columns \
                                  or str2 in dataframes[3].columns \
                                  or str3 in dataframes[3].columns \
                                  or str4 in dataframes[3].columns or str5 in dataframes[3].columns or str6 in
                                  dataframes[3].columns \
                                  or str7 in dataframes[3].columns or str8 in dataframes[3].columns or str9 in
                                  dataframes[3].columns \
                                  or str10 in dataframes[3].columns or str11 in dataframes[3].columns or str12 in
                                  dataframes[3].columns \
                                  or str13 in dataframes[3].columns or str14 in dataframes[3].columns or str15 in
                                  dataframes[3].columns \
                                  or str16 in dataframes[3].columns or str17 in dataframes[3].columns or str18 in
                                  dataframes[3].columns \
                                  or str19 in dataframes[3].columns or str20 in dataframes[3].columns or str21 in
                                  dataframes[3].columns \
                                  or str22 in dataframes[3].columns or str23 in dataframes[3].columns or str24 in
                                  dataframes[3].columns \
                                  or str25 in dataframes[3].columns or str26 in dataframes[3].columns):
        this_data = pd.DataFrame(dataframes[3])
        three = True
    if len(dataframes) > 2:

        if "ARTÍCULO" in dataframes[2].columns or "MM Num. articulo" in dataframes[2].columns or "MM Num. artículo" in \
                dataframes[2].columns or 'CÓDIGO' in dataframes[2].columns or 'MM Num.' in dataframes[
            2].columns or str3 in \
                dataframes[2].columns or str4 in dataframes[2].columns or str5 in dataframes[2].columns or str6 in \
                dataframes[2].columns or str7 in dataframes[2].columns or str8 in dataframes[2].columns or str9 in \
                dataframes[2].columns or str10 in dataframes[2].columns or str11 in dataframes[2].columns or str12 in \
                dataframes[2].columns or str13 in dataframes[2].columns or str14 in dataframes[2].columns or str15 in \
                dataframes[2].columns or str16 in dataframes[2].columns or str17 in dataframes[2].columns or str18 in \
                dataframes[2].columns or str19 in dataframes[2].columns or str20 in dataframes[2].columns:
            this_data = pd.DataFrame(dataframes[2])
            two = True

    if len(dataframes) > 3:
        if "ARTÍCULO" in dataframes[3].columns or "MM Num. articulo" in dataframes[3].columns or "MM Num. artículo" in \
                dataframes[3].columns or 'CÓDIGO' in dataframes[3].columns or 'MM Num.' in dataframes[
            3].columns or str3 in dataframes[3].columns or str4 in dataframes[3].columns or str5 in dataframes[
            3].columns or str6 in dataframes[3].columns or str7 in dataframes[3].columns or str8 in dataframes[
            3].columns or str9 in dataframes[3].columns or str10 in dataframes[3].columns or str11 in dataframes[
            3].columns or str12 in dataframes[3].columns or str13 in dataframes[3].columns or str14 in dataframes[
            3].columns or str15 in dataframes[3].columns or str16 in dataframes[3].columns or str17 in dataframes[
            3].columns or str18 in dataframes[3].columns or str19 in dataframes[3].columns or str20 in dataframes[
            3].columns:
            this_data = pd.DataFrame(dataframes[3])
            three = True
    below_table = ''
    if len(dataframes) > 1:
        if zero:
            below_table = dataframes[1]

    if len(dataframes) > 2:
        if one:
            below_table = dataframes[2]

    if len(dataframes) > 3:
        if two:
            below_table = dataframes[3]

    if len(dataframes) > 3:
        if three:
            below_table = dataframes[4]

    df2 = None

    if this_data is None:
        pass
    else:
        if this_data.shape[1] > 4:
            try:
                this_data.columns = this_data.columns.str.replace('SELECTED  ', '')
                this_data.columns = this_data.columns.str.replace('SELECTED ', '')
                this_data.columns = this_data.columns.str.replace('SELECTED', '')
                this_data.columns = this_data.columns.str.replace('NOT_', '')
                this_data.columns = this_data.columns.str.replace('NOT_SELECTED  ', '')
                this_data.columns = this_data.columns.str.replace('NOT_SELECTED', '')
                big = this_data.columns[0]
                cont = this_data.columns[2]
                lot = this_data.columns[1]
                prec = this_data.columns[3]
                cant = this_data.columns[-5]
                imp = this_data.columns[-2]
                importe = this_data.columns[-3]
                third = this_data.columns[-4]
                this_data = this_data.loc[
                    (this_data[big] != "Número de pedido") & (this_data[big] != "*** Número de pedido") & (
                            this_data[big] != "*** Número de") & (this_data[big] != "*** Número")]
                this_data = this_data.loc[
                    (this_data[big] != "Entregado a: TABERNA") & (this_data[big] != "Entregado a: TASCA") & (
                            this_data[big] != "Entregado a: TABERNA OSUNA")
                    & (this_data[big] != "Entregado a: TABERNA osuna") & (this_data[big] != "Fin de número")]
                this_data = this_data.loc[(this_data[imp] != "Spain Fecha:") & (this_data[imp] != "Spain Fecha:0") & (
                        this_data[imp] != "Spain Fecha:1")]
                this_data = this_data.loc[this_data[cont] != "LOT:"]
                this_data = this_data.loc[this_data[cant] != "Total"]
                this_data = this_data.loc[this_data[cant] != "LA LAGUNA"]
                this_data = this_data.replace('', np.nan)
                this_data = this_data.dropna(axis=0, thresh=3, how="any")
                limitPer = len(this_data) * .100
                this_data = this_data.dropna(thresh=limitPer, axis=1)
                this_data = this_data.replace(np.nan, '0')
            except:
                pass
            data = this_data
            big = this_data

            # for  second column
            this_data["second_count"] = this_data.iloc[:, 1].str.count("\D")
            this_data["second_length"] = this_data.iloc[:, 1].str.len()
            this_data["second_digit_percentage"] = this_data["second_count"] / this_data["second_length"] * 100
            # for third column
            this_data["third_count"] = this_data.iloc[:, 2].str.count("\D")
            this_data["third_length"] = this_data.iloc[:, 2].str.len()
            this_data["third_digit_percentage"] = this_data["third_count"] / this_data["third_length"] * 100
            # for  forth column
            dftwo = False
            if len(data.columns) == 3:
                this_data["forth_count"] = this_data.iloc[:, 3].str.count("\D")
                this_data["forth_length"] = this_data.iloc[:, 3].str.len()
                this_data["forth_digit_percentage"] = this_data["forth_count"] / this_data["forth_length"] * 100
                dftwo = True

            this_data.fillna(0)

            df = this_data.query("second_digit_percentage>30.0")
            df1 = this_data.query("third_digit_percentage>30.0")
            if dftwo:
                df2.fillna(0)
                df2 = this_data.query("forth_digit_percentage>60.0")
            desc = ''
            if len(df) == len(this_data):
                desc = df.iloc[:, 1]

            elif len(df1) == len(this_data):
                desc = df1.iloc[:, 2]

            elif len(df2) == len(this_data):
                desc = df2.iloc[:, 3]

            desc_data = pd.DataFrame()
            if len(desc) != 0:
                desc_data = pd.DataFrame(desc)
                desc_data.head()

            code = this_data.iloc[:, 0]
            codingo_data = pd.DataFrame(code)

            prec = []
            str1 = "Precio"
            str2 = "Base I"
            str3 = "PVP"
            str4 = 'Importe'
            str5 = 'Euro Uni.'
            str6 = "IMP"
            price = ''
            for i in this_data.columns:
                ratio1 = fuzz.partial_ratio(str1.lower(), str(i).lower())
                if ratio1 >= 75:
                    prec.append(i)
                    price = i

                ratio2 = fuzz.partial_ratio(str2.lower(), str(i).lower())
                if ratio2 >= 75:
                    prec.append(i)
                    price = i

                ratio3 = fuzz.partial_ratio(str3.lower(), str(i).lower())
                if ratio3 >= 75:
                    prec.append(i)
                    price = i
                ratio4 = fuzz.partial_ratio(str4.lower(), str(i).lower())
                if ratio4 >= 75:
                    prec.append(i)
                    price = i
                ratio5 = fuzz.partial_ratio(str5.lower(), str(i).lower())
                if ratio5 >= 75:
                    prec.append(i)
                    price = i
                ratio6 = fuzz.partial_ratio(str6.lower(), str(i).lower())
                if ratio6 >= 75:
                    prec.append(i)
                    price = i
            if len(prec) > 1:
                price = prec[0]
            else:
                pass
            if price == '':
                pass
            else:
                price_col = this_data[price]
                price_data = pd.DataFrame(price_col, columns=[price])

            str1 = "DTO"
            str2 = "Descuento"
            str3 = "DCTO"
            str4 = "Desc"
            disc = ''
            for i in this_data.columns:
                ratio1 = fuzz.ratio(str1.lower(), str(i).lower())
                ratio2 = fuzz.ratio(str2.lower(), str(i).lower())
                ratio3 = fuzz.ratio(str3.lower(), str(i).lower())
                ratio4 = fuzz.ratio(str4.lower(), str(i).lower())
                if ratio1 >= 75:

                    disc = i


                elif ratio2 >= 75:

                    disc = i


                elif ratio3 >= 75:

                    disc = i


                elif ratio4 >= 75:

                    disc = i

            if disc != '':
                disc_col = this_data[disc]
                disc_data = pd.DataFrame(disc_col, columns=[disc])

            str1 = "Cantidad"
            str2 = "Cant"
            str3 = "Unid"
            str4 = "Unidades"
            str5 = "Uds"
            str6 = "Peso"
            cat = ""
            for i in this_data.columns:
                ratio1 = fuzz.ratio(str1.lower(), str(i).lower())
                if ratio1 >= 75:
                    cat = i

                ratio2 = fuzz.ratio(str2.lower(), str(i).lower())
                if ratio2 >= 75:
                    cat = i

                ratio3 = fuzz.ratio(str3.lower(), str(i).lower())
                if ratio3 >= 75:
                    cat = i
                ratio4 = fuzz.ratio(str4.lower(), str(i).lower())
                if ratio4 >= 75:
                    cat = i
                ratio5 = fuzz.ratio(str5.lower(), str(i).lower())
                if ratio5 >= 75:
                    cat = i
                ratio6 = fuzz.ratio(str6.lower(), str(i).lower())
                if ratio6 >= 75:
                    cat = i
            if cat == '':
                pass
            else:
                Cantidad = this_data[cat]
                Cantidad_data = pd.DataFrame(Cantidad, columns=[cat])

            str1 = 'IMPUESTO'
            imposto = ''

            for i in this_data.columns:
                ratio1 = fuzz.ratio(str1.lower(), str(i).lower())
                if ratio1 >= 75:
                    imposto = i

            if imposto != '':
                imposto_col = this_data[imposto]
                imposto_data = pd.DataFrame(imposto_col, columns=[imposto])

            str1 = 'Tasa'
            str2 = 'TIPO'
            tasa = ''
            for i in this_data.columns:
                ratio1 = fuzz.partial_ratio(str1.lower(), str(i).lower())
                if ratio1 >= 75:
                    tasa = i
                ratio2 = fuzz.ratio(str2.lower(), str(i).lower())
                if ratio2 >= 75:
                    tasa = i

            if tasa != '':
                tasa_col = this_data[tasa]
                tasa_data = pd.DataFrame(tasa_col, columns=[tasa_col])

            df2 = this_data
            if disc == '' and imposto == '' and tasa == '':
                df2 = pd.concat([codingo_data, desc_data, Cantidad_data, price_data], axis=1, join='inner')
                df2['Discount'] = 0
                df2['IMPUESTO'] = 0
                df2['Tasa'] = 0

            elif disc == '' and imposto == '' and tasa == '' and cant == '' and price == '':
                df2 = pd.concat([codingo_data, desc_data], axis=1, join='inner')
                df2['Price'] = 0
                df2['Quantity'] = 0
                df2['Discount'] = 0
                df2['IMPUESTO'] = 0
                df2['Tasa'] = 0
            elif disc == '' and imposto == '' and tasa == '' and desc == '':
                df2 = pd.concat([codingo_data, Cantidad_data, price_data], axis=1, join='inner')
                df2["Description"] = ''
                df2['Discount'] = 0
                df2['IMPUESTO'] = 0
                df2['Tasa'] = 0

            elif disc != '' and imposto == '' and tasa == '':
                disc_col = this_data[disc]
                disc_data = pd.DataFrame(disc_col, columns=[disc])
                df2 = pd.concat([codingo_data, desc_data, Cantidad_data, price_data, disc_data], axis=1, join='inner')
                df2['IMPUESTO'] = 0
                df2['Tasa'] = 0

            elif disc != '' and imposto != '' and tasa == '':
                disc_col = this_data[disc]
                disc_data = pd.DataFrame(disc_col, columns=[disc])
                df2 = pd.concat([codingo_data, desc_data, Cantidad_data, price_data, disc_data, imposto_data], axis=1,
                                join='inner')
                df2['Tasa'] = 0

            elif disc != '' and imposto == '' and tasa != '':
                disc_col = this_data[disc]
                disc_data = pd.DataFrame(disc_col, columns=[disc])
                df2 = pd.concat([codingo_data, desc_data, Cantidad_data, price_data, disc_data, tasa_data], axis=1,
                                join='inner')
                df2['IMPUESTO'] = 0

            elif disc == '' and imposto != '' and tasa != '':
                df2 = pd.concat([codingo_data, desc_data, Cantidad_data, price_data, imposto_data, tasa_data], axis=1,
                                join='inner')
                df2['Discount'] = 0

            elif disc == '' and imposto != '' and tasa == '':
                df2 = pd.concat([codingo_data, desc_data, Cantidad_data, price_data, imposto_data], axis=1, join='inner')
                df2['Discount'] = 0

            # data['vat_number']= data['vat_number'].str.replace(',', '')
            df2 = df2.replace('', 0)
            df2.columns.values[0] = "Codigo"
            df2.columns.values[1] = "Description"
            df2.columns.values[2] = "Cantidad"
            df2.columns.values[3] = "Precio"
            df2.columns.values[4] = "Discount"

            df2.iloc[:, 2] = df2.iloc[:, 2].apply(lambda x: x.split(' ')[0].replace('[A-Z]', ''))

            df2.iloc[:, 2] = df2.iloc[:, 2].apply(lambda x: x.split(' ')[0].replace('[/\+%&*-]', ''))
            df2.iloc[:, 3] = df2.iloc[:, 3].apply(lambda x: x.split(' ')[0].replace('[A-Z]', ''))
            df2.iloc[:, 3] = df2.iloc[:, 3].apply(lambda x: x.split(' ')[0].replace('[/\+%&*-]', ''))
            print(df2.iloc[:, 2])
            print(df2.iloc[:, 3])
            sys.exit()

            df2.iloc[:, 2] = df2.iloc[:, 2].apply(lambda x: x.split(' ')[0].replace(',', '.'))
            df2.iloc[:, 3] = df2.iloc[:, 3].apply(lambda x: x.split(' ')[0].replace(',', '.'))
            # df2.iloc[:, 4] = float(df2.iloc[:, 4].iloc[0].split(' ')[0].replace(',', '.'))

    if df2 is None or len(df2) < 1:
        structData['tables'] = {
            'shape': [0, 0],
            'header': ["Codigo", "Description", "Cantidad", "Precio", "Discount", "IMPUESTO", "Tasa"],
            'dataframes': [
                {"Codigo": {}, "Description": {}, "Cantidad": {}, "Precio": {}, "Discount": {}, "IMPUESTO": {},
                 "Tasa": {}}],
            'bases''': {'igic': {'0': 0, '3': 0, '7': 0, '15': 0, '20': 0}, 'iva': {'4': 0, '10': 0, '21': 0}}, 'sup': 0, 'ret': 0
        }
    else:
        # print(f'Printing table for debug: {table}')
        objdf = df2.to_dict()

        structData['tables'] = {
            'shape': list(df2.shape),
            'header': list(df2.columns),
            'dataframes': [objdf],
            'bases''': {'igic': {'0': 0, '3': 0, '7': 0, '15': 0, '20': 0}, 'iva': {'4': 0, '10': 0, '21': 0}}, 'sup': 0, 'ret': 0
        }

    if df2 is not None:
        for row in df2.itertuples():
            quantity = float((row[3]))
            price = float((row[4]))
            discount = float((row[5]))
            tax = float((row[7]))
            row_total = (quantity * (price - (1 - (discount/100))) * ( 1 + (tax/100)))

            print(str(structData['labels']['total']) + '<=>' + str(row_total))

            if str(structData['labels']['total']) == str(row_total):
                structData['labels']['inv_validation'] = 1
    else:
        print('no se hizo la comprobación')

    print(json.dumps(structData))
    print('===============================================')

    return structData
