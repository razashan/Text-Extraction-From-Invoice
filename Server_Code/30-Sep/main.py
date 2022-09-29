
from __future__ import absolute_import

import re
import os
import sys

from pdf2image import convert_from_path
import pytesseract
import math
import cv2
import datetime
from PyPDF2 import PdfFileReader, PdfFileWriter
from readImage import read_image

def split_pdf(doc_name):
    pageList = os.listdir('pages')
    for eachPage in pageList:
        os.remove('pages\\'+eachPage)

    fname = os.path.splitext(os.path.basename(doc_name))[0]
    pdf = PdfFileReader(doc_name, strict=False)
    for page in range(pdf.getNumPages()):
        strPage = str(page + 1).zfill(3)
        pdf_writer = PdfFileWriter()
        pdf_writer.addPage(pdf.getPage(page))
        output_filename = fname+'_'+str(strPage)+'.pdf'
        with open('pages\\'+output_filename, 'wb') as out:
            pdf_writer.write(out)

def find_amounts(text):
    amounts = re.findall(r'\d+\.\d{2}\b', text)
    floats = [float(amount) for amount in amounts]
    unique = list(dict.fromkeys(floats))
    if len(unique) == 0:
        return 0
    else:
        return max(unique)

def clasificator_tesseract_document(pdf_file, cif):
    in_path = str(pdf_file)
    output_folder = ('\\'.join(in_path.split('\\')[:-1]))

    print('Procesando pagina '+in_path)

    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'


    convert_from_path(in_path, output_folder=output_folder, single_file=True, fmt='png', output_file=in_path)

    Ima = str(in_path) + '.png'

    dat = {
        "vat_number": '',
        "total":  '',
        "date": '',
        "document_type": '',
        "document_type_id": '',
        "invoice_number": '',
        "vat_validation": 0,
        "inv_validation": 0}

    # Convert file to image
    img = cv2.imread(Ima, cv2.COLOR_RGB2GRAY)

    # Extract text from image
    #pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    text = (pytesseract.image_to_string(img))
    text_list = text.split("\n")
    vat = ''
    date = []
    doc_type = []
    doc_type_id = []

    dat['total'] = find_amounts(text.replace(',', '.'))
    for idx, a in enumerate(text_list):
        if (a.strip() != ""):

            if (re.search("[A-Z]{1}-[0-9]{8}", a)):
                b = re.findall("[A-Z]{1}-[0-9]{8}", a)
                vat = (b[0].replace('-', ''))
            elif (re.search("[A-Z]-[0-9][0-9]\/[0-9][0-9][0-9][0-9][0-9][0-9]", a)):
                b = re.findall("[A-Z]-[0-9][0-9]\/[0-9][0-9][0-9][0-9][0-9][0-9]", a)
                vat = b[0].replace('-', '').replace('/', '').replace('-', '')
            elif (re.search("[0-9]{8}-[A-Z]{1}", a)):
                b = re.findall("[0-9]{8}-[A-Z]{1}", a)
                vat = b[0].replace('-', '')
            elif (re.search("[0-9]{8}[A-Z]{1}", a)):
                b = re.findall("[0-9]{8}[A-Z]{1}", a)
                vat = b[0]
            elif (re.search("[A-Z]{1}-[0-9]{8}", a)):
                b = re.findall("[A-Z]{1}-[0-9]{8}", a)
                vat = b[0].replace('-', '')
            elif (re.search("[A-Z]{1}[0-9]{8}", a)):
                b = re.findall("[A-Z]{1}[0-9]{8}", a)
                vat = b[0]
            elif (re.search("[A-Z]{1}[0-9]{2}/[0-9]{6}", a)):
                b = re.findall("[A-Z]{1}[0-9]{2}/[0-9]{6}", a)
                vat = b[0].replace('/', '')
            elif (re.search("[A-Z]{1}-[0-9]{2}.[0-9]{3}.[0-9]{3}", a)):
                b = re.findall("[A-Z]{1}-[0-9]{2}.[0-9]{3}.[0-9]{3}", a)
                vat = b[0].replace('-', '')
            elif (re.search("[A-Z]{1}-[0-9]{2}/[0-9]{6}", a)):
                b = re.findall("[A-Z]{1}-[0-9]{2}/[0-9]{6}", a)
                vat = b[0].replace('-', '')

            if dat["vat_number"] == '' and vat != cif:
                dat["vat_number"] = vat

            if "ALBARAN" in a or "Albaran" in a or "Albarán" in a or "ALBARÁN" in a:
                dat["document_type"] = "Albaran"
                dat["document_type_id"] = 3
                doc_type.append("Albaran")
                doc_type_id.append(3)
            elif "Factura" in a or "FACTURA" in a and ("Rectificativa" not in a or "RECTIFICATIVA" not in a):
                dat["document_type"] = "Factura"
                dat["document_type_id"] = 6
                doc_type.append("Factura")
                doc_type_id.append(6)
            elif "Rectificativa" in a or "RECTIFICATIVA" in a or "ABONO" in a or "Abono" in a:
                dat["document_type"] = "Factura Rectificativa"
                dat["document_type_id"] = 7
                doc_type.append("Factura Rectificativa")
                doc_type_id.append(7)

            if len(doc_type) > 1:
                dat["document_type"] = doc_type[0]
                dat["document_type_id"] = doc_type_id[0]

            if (re.search("\d{2}/\d{2}/\d{4}", a)):
                b = re.findall("\d{2}/\d{2}/\d{4}", a)
                dat["date"] = b[0].replace('/', '-')
                date.append(b[0].replace('/', '-'))
            elif (re.search("\d{2}-\d{2}-\d{4}", a)):
                b = re.findall("\d{2}-\d{2}-\d{4}", a)
                dat["date"] = b[0]
                date.append(b[0])
            elif (re.search("\d{2}-\d{2}-\d{2}", a)):
                b = re.findall("\d{2}-\d{2}-\d{2}", a)
                dat["date"] = b[0]
                date.append(b[0])
            elif (re.search("\d{2}/\d{2}/\d{2}", a)):
                b = re.findall("\d{2}/\d{2}/\d{2}", a)
                dat["date"] = b[0].replace('/', '-')
                date.append(b[0].replace('/', '-'))
            elif (re.search("\d{1}/\d{2}/\d{2}", a)):
                b = re.findall("\d{1}/\d{2}/\d{2}", a)
                dat["date"] = b[0]
                date.append(b[0].replace('/', '-'))
            elif (re.search("[0-9]{2}\.[0-9]{2}\.[0-9]{4}", a)):
                b = re.findall("[0-9]{2}\.[0-9]{2}\.[0-9]{4}", a)
                dat["date"] = b[0].replace('.', '-')
                date.append(b[0].replace('.', '-'))

            if len(date) > 1:
                dat["date"] = date[0]


            if ("Factura" in a or "ALBARAN" in a):
                b = a.split(" ")
                if b[0] == "ALBARAN":
                    dat["invoice_number"] = b[0]

                if len(b) > 3:

                    if len(b) > 4 and b[2] != '—' and len(b[1]) != 25 and len(b[1]) > 5:
                        dat["invoice_number"] = b[1] + b[2]
                    elif len(b) >= 5 and len(b[1]) == 25:
                        dat["invoice_number"] = b[1]
                    elif len(b) > 6 and len(b[3]) > 15:
                        dat["invoice_number"] = b[1] + b[2] + b[3]
                    elif len(b) > 6 and b[1] == "0/0":
                        dat["invoice_number"] = b[1] + b[2]


    if len(dat['date']) == 10:
        pass
    elif len(dat['date']) == 8:
        dat['date'] = dat['date'][0:6] + '20' + dat['date'][6:]


    # dat["invoice_number"] = ''
    # prov = Company.objects.filter(cif=dat["vat_number"])
    # if len(prov) > 0:
    #     patterns_list = Patterns_cif.objects.filter(company=prov[0])
    #     for idx, a in enumerate(text_list):
    #         if (a.strip() != ""):
    #             for each_pattern in patterns_list:
    #                 noblanks = a.replace(' ', '')
    #                 the_pattern = each_pattern.pattern
    #                 if (re.search(the_pattern, noblanks)):
    #                     dat["invoice_number"] = re.findall(the_pattern, noblanks)[0]
    #                     print('encontrado el numero ' + dat["invoice_number"] + ' con patron ' + the_pattern + ' para el proveedor ' + str(prov[0].id))


    structData = {}
    structData['labels'] = dat
    structData['tables'] = {}


    try:
        splitted = dat['date'].split('-')
        formated_date = str(splitted[2]) + '-' + str(splitted[1]) + '-' + str(splitted[0])
        datetime.datetime.strptime(formated_date, '%Y-%m-%d')
    except:
        formated_date = None


    try:
        if math.isnan(dat['document_type_id']):
            document_type_id = None
        else:
            document_type_id = dat['document_type_id']
    except:
        document_type_id = None

    read_image(Ima, structData)

    return dat


CURR_DIR = os.path.dirname(os.path.realpath(__file__))

fileList = os.listdir('file')
for eachFile in fileList:
    full_path = (CURR_DIR + '\\file\\' + eachFile)
    split_pdf(full_path)

pageList = os.listdir('pages')
for eachPage in pageList:
    full_path = (CURR_DIR + '\\pages\\' + eachPage)
    if eachFile.endswith('.pdf'):
        try:
            #TODO: Remember to include the CLIENT´S VAT number as a parameter
            clasificator_tesseract_document(full_path, 'B65258568')
        except Exception as ex:
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "line": tb.tb_lineno
                })
                tb = tb.tb_next
            print('type: ' + type(ex).__name__)
            print('message: ' + str(ex))
            for eachTrace in trace:
                print(str(eachTrace))
            print('===============================================')
            #sys.exit()
