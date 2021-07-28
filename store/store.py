from django.views.generic import View
import xlrd
import openpyxl

from .models import Author, Publisher, Categorie, Ouvrage

class xlsx():

    def importXLSX(self, file):
        # f = xlrd.open_workbook(file_contents=file.read())
        wb = openpyxl.load_workbook(file, data_only=True)
        # # Table Catégorie
        # catSheet = wb.get_sheet_by_name("categorie")
        # for r in range(2, catSheet.max_row):
        #     cat = catSheet.cell(row=r, column=2).value
        #     categorie = Categorie()
        #     categorie.name = cat
        #     categorie.save()
# 
        # pubSheet = wb.get_sheet_by_name("editeur")
        # for r in range(2, pubSheet.max_row):
        #     pubName = pubSheet.cell(row=r, column=2).value
        #     pubMarge = pubSheet.cell(row=r, column=3).value
        #     publisher = Publisher()
        #     publisher.name = pubName
        #     publisher.marge = pubMarge
        #     publisher.save()
# 
        # autSheet = wb.get_sheet_by_name("auteur")
        # for r in range(2, autSheet.max_row):
        #     autName = autSheet.cell(row=r, column=2).value
        #     autForname = autSheet.cell(row=r, column=3).value
        #     author = Author()
        #     author.name = autName
        #     author.forname = autForname
        #     author.save()

        ouvSheet = wb.get_sheet_by_name("ouvrage")
        for r in range(2, ouvSheet.max_row):
            # with transaction.atomic():
            ouvrage = Ouvrage()
            ouvRef = ouvSheet.cell(row=r, column=2).value
            ouvrage.reference=ouvRef
            ouvrage.save()
            ouvTitle = ouvSheet.cell(row=r, column=3).value
            ouvrage.title=ouvTitle
            ouvPub = ouvSheet.cell(row=r, column=4).value
            print(ouvTitle)
            pubObj = Publisher.objects.filter(name=ouvPub).first()
            if pubObj != None:
                ouvrage.editeurs.add(pubObj.id)
            ouvAuthors = ouvSheet.cell(row=r, column=5).value
            for author in ouvAuthors.split(' et '):
                autName = author.split(', ')[0]
                autForname = author.split(', ')[1]
                if autForname != "":
                    autObj = Author.objects.filter(name=autName, forname=autForname).first()
                else:
                    autObj = Author.objects.filter(name=autName).first()
                ouvrage.auteurs.add(autObj.id)
            ouvCats = ouvSheet.cell(row=r, column=6).value
            catObj = Categorie.objects.filter(name=ouvCats).first()
            if catObj != None:
                ouvrage.categories.add(catObj.id)
            ouvPar = ouvSheet.cell(row=r, column=7).value
            ouvrage.publication=ouvPar
            ouvPrice = ouvSheet.cell(row=r, column=8).value
            ouvrage.price=ouvPrice
            ouvStock = ouvSheet.cell(row=r, column=11).value
            if ouvStock == "":
                ouvrage.stock=0
            else:
                ouvrage.stock=ouvStock
            ouvPic = ouvSheet.cell(row=r, column=12).value
            if ouvPic == "":
                ouvrage.picture = None
            else:
                ouvrage.picture=ouvPic
            ouvNote = ouvSheet.cell(row=r, column=13).value
            ouvrage.note=ouvNote
            ouvrage.save()

    def exportXLSX(self):
        pass