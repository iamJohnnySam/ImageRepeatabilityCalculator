import os
from datetime import datetime
from pylatex import Document, Command, Section, Subsection, Tabular
from pylatex import Math, TikZ, Axis, Plot, Figure, Matrix, Alignat
from pylatex.utils import italic


class Documenter:
    def __init__(self, serial, author):
        self.document_name = serial + "REPEATABILITY TEST"

        self.doc = Document(documentclass='article')
        self.doc.preamble.append(Command('input', 'latex_files/use_packages'))
        self.doc.preamble.append(Command('input', 'latex_files/BoxStyle'))
        self.doc.preamble.append(Command('input', 'latex_files/def_theme'))

        self.doc.set_variable("Year", str(datetime.today().year))
        self.doc.set_variable("date", str(datetime.today()))
        self.doc.set_variable("EFEMMachine", serial)
        self.doc.set_variable("DocumentName", self.document_name)
        self.doc.set_variable("DocumentNumber", self.document_name)
        self.doc.set_variable("DocumentRevision", self.get_revision())

        self.doc.set_variable("Author", author)

    def get_revision(self):
        revision = 0
        while revision < 100:
            doc = self.document_name + "-" + "%02d" % (revision,)
            if os.path.isfile("document/" + doc + ".pdf"):
                revision = revision + 1
            else:
                break

        return "%02d" % (revision,)

    def create_document(self, ):
        self.doc.append(Command('input', 'latex_files/base_doc'))
        self.doc.generate_pdf('full', clean_tex=False)
