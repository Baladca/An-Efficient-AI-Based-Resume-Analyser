import os
import io
import spacy
import multiprocessing as mp
import pprint
from spacy.matcher import Matcher
from . import utils

class CertificateParser(object):

    def __init__(
        self,
        certificate,
        custom_regex=None
    ):
        nlp = spacy.load('en_core_web_sm')
        custom_nlp = spacy.load(os.path.dirname(os.path.abspath(__file__)))
        self.__custom_regex = custom_regex
        self.__matcher = Matcher(nlp.vocab)
        self.__details = {
            'name': None,
            'date': None,
            'course': None,
            'organization': None,
            'certificate_number': None,
        }
        self.__certificate = certificate
        if not isinstance(self.__certificate, io.BytesIO):
            ext = os.path.splitext(self.__certificate)[1].split('.')[1]
        else:
            ext = self.__certificate.name.split('.')[1]
        self.__text_raw = utils.extract_text(self.__certificate, '.' + ext)
        self.__text = ' '.join(self.__text_raw.split())
        self.__nlp = nlp(self.__text)
        self.__custom_nlp = custom_nlp(self.__text_raw)
        self.__noun_chunks = list(self.__nlp.noun_chunks)
        self.__get_basic_details()

    def get_extracted_data(self):
        return self.__details

    def __get_basic_details(self):
        # Implement methods to extract details from the certificate
        # For example: extract_name(), extract_date(), extract_course(), etc.
        # Utilize patterns, rules, or other techniques depending on the certificate structure and content
        # Populate self.__details with extracted information
        return


def certificate_result_wrapper(certificate):
    parser = CertificateParser(certificate)
    return parser.get_extracted_data()

if __name__ == '__main__':
    # Multiprocessing part can be similar to the resume parser script
    pool = mp.Pool(mp.cpu_count())

    certificates = []
    data = []
    for root, directories, filenames in os.walk('certificates'):
        for filename in filenames:
            file = os.path.join(root, filename)
            certificates.append(file)

    results = [
        pool.apply_async(
            certificate_result_wrapper,
            args=(x,)
        ) for x in certificates
    ]

    results = [p.get() for p in results]

    pprint.pprint(results)
