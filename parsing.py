import re
import os
import zipfile
import string 
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

# Regular expressions to extract data from the corpus
doc_regex = re.compile("<DOC>.*?</DOC>", re.DOTALL)
docno_regex = re.compile("<DOCNO>.*?</DOCNO>")
text_regex = re.compile("<TEXT>.*?</TEXT>", re.DOTALL)


with zipfile.ZipFile("ap89_collection_small.zip", 'r') as zip_ref:
    zip_ref.extractall()
   
# Retrieve the names of all files to be indexed in folder ./ap89_collection_small of the current directory
for dir_path, dir_names, file_names in os.walk("ap89_collection_small"):
    allfiles = [os.path.join(dir_path, filename).replace("\\", "/") for filename in file_names if (filename != "readme" and filename != ".DS_Store")]
    
for file in allfiles:
    with open(file, 'r', encoding='ISO-8859-1') as f:
        filedata = f.read()
        result = re.findall(doc_regex, filedata)  # Match the <DOC> tags and fetch documents

        for document in result[0:]:
            # Retrieve contents of DOCNO tag
            docno = re.findall(docno_regex, document)[0].replace("<DOCNO>", "").replace("</DOCNO>", "").strip()
            # Retrieve contents of TEXT tag
            text = "".join(re.findall(text_regex, document))\
                      .replace("<TEXT>", "").replace("</TEXT>", "")\
                      .replace("\n", " ")
            # step 1 - lower-case words, remove punctuation, remove stop-words, etc. 
            text = text.lower()
            print(text.islower())
            text = text.translate(str.maketrans('', '', string.punctuation))
            # print('\n\n\n\n')
            # print(text)

            nltk.download('stopwords')
            nltk.download('punkt')
            nltk.download('wordnet')
            # print('\n\n\n\n')
            # print(tokens_without_sw)
            text_tokens = word_tokenize(text)
            tokens_without_sw = [word for word in text_tokens if not word in stopwords.words()]
            
            print('\n\n\n\n')
            print(tokens_without_sw)

            lemma = nltk.wordnet.WordNetLemmatizer()
            tokens_without_sw = lemma.lemmatize(tokens_without_sw)

            print('\n\n\n\n')
            print(tokens_without_sw)

            # step 2 - create tokens 

            


            # step 3 - build index
            