import re
import os
import zipfile
import string
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

# Regular expressions to extract data from the corpus
doc_regex = re.compile("<DOC>.*?</DOC>", re.DOTALL)
docno_regex = re.compile("<DOCNO>.*?</DOCNO>")
text_regex = re.compile("<TEXT>.*?</TEXT>", re.DOTALL)

#zip extract function, uncomment out later
# with zipfile.ZipFile("ap89_collection_small.zip", 'r') as zip_ref:
#     zip_ref.extractall()

#map term to an id
term_ids = {}
#map document name to document id
doc_ids = {}
# key:term_id, value:(doc#, frequency in document, [ position1, position2, .....] )
term_info = {}
#unique ids
doc_uid = 1
term_uid = 1000

print('Preparing...\n')

#open stopwords.txt file and read it
with open("stopwords.txt", 'r') as sw_text:
        stopwords = sw_text.read().split()
        #print(stopwords)

# Retrieve the names of all files to be indexed in folder ./ap89_collection_small of the current directory
for dir_path, dir_names, file_names in os.walk("ap89_collection_small"):
    allfiles = [os.path.join(dir_path, filename).replace("\\", "/") for filename in file_names if
                (filename != "readme" and filename != ".DS_Store")]

for file in allfiles:
    with open(file, 'r', encoding='ISO-8859-1') as f:
        filedata = f.read()
        result = re.findall(doc_regex, filedata)  # Match the <DOC> tags and fetch documents

        for document in result[0:]:
            # Retrieve contents of DOCNO tag
            docno = re.findall(docno_regex, document)[0].replace("<DOCNO>", "").replace("</DOCNO>", "").strip()
            # Retrieve contents of TEXT tag
            text = "".join(re.findall(text_regex, document)) \
                .replace("<TEXT>", "").replace("</TEXT>", "") \
                .replace("\n", " ")

            # step 1 - lower-case words, remove punctuation, remove stop-words, etc.
            #make text into lower case
            text = text.lower()
            #remove all punctuations
            text = text.translate(str.maketrans('', '', string.punctuation))
            
            # text_new_regex = re.compile("\w+([\,\.]\w+)*")
            # text_new = re.findall(text_new_regex, text)

            #tokenize the text
            text_tokens = word_tokenize(text)

            # print("original:\n")
            # print(text_tokens)
            # print('\n')
            # text_new = word_tokenize(text_new)
            # print("new:\n")
            # print(text_new)


            #remove all stopwords from stopwords.txt file
            text_tokens_without_sw = [word for word in text_tokens if word not in stopwords]
            # for word in text_tokens:
            #     if(word not in stopwords):
            #         text_tokens_without_sw.append(word)
            # print(text_tokens_without_sw)
            # print('\n\n\n\n')

            #apply stemming to tokens
            porter = PorterStemmer()
            unique_terms = set()
            text_stemmed_sw = []
            for word in text_tokens_without_sw:
                unique_terms.add(word)
                text_stemmed_sw.append(porter.stem(word))


            # step 2 - create tokens
            pos = 1
            
            # print(len(unique_terms))
            # print(docno.lower())
            # print("docno: ", docno)
            # print("doc name: ", os.path.basename(f.name))
            #map key:doc id with value:doc uid
            # print(type(doc_ids))
            
            doc_ids[docno.lower()] = {'doc_uid': doc_uid, 'total_terms': len(text_stemmed_sw), 'unique_terms': len(unique_terms)}

            # print('l')
            # for key in doc_ids:
            #     print(type(key))
            #     print(key)


            # key:term_id, value:(doc#, frequency in document, [ position1, position2, .....] )
            # term_info = {}
            #map term to an id
            # term_ids = {}
            #map document name to document id
            # doc_ids = {}

            #create the index
            for word in text_stemmed_sw:
                if word not in term_ids:                                          #if word not in term_ids, then add it to the dict 
                    term_info[word] = [{'docno': docno, 'freq': 1, 'pos': [pos]}] #adding word to dict with term_uid as key
                    term_ids[word] = {term_uid}                                   #adding word key to term_id value

                elif term_info[word][-1]['docno'] == docno:                       #check if the current docno matches the docno in the last entry to update the freq and pos of word
                    # print("dup word: ", word) #temp
                    term_info[word][-1]['freq'] += 1
                    term_info[word][-1]['pos'].append(pos)

                else:                                                             #word is in term_ids, add a new doc entry of the word
                    term_info[word].append({'docno': docno, 'freq': 1, 'pos': [pos]})
                pos += 1
                term_uid += 1

            # print("here")
            doc_uid += 1
            
            #looks at every word and puts them into term_info
            # for word in text_stemmed_sw:
            #     if word not in term_info.values(): #if word not in term_info, then add it to the dict 
            #         term_info[term_uid] = [{'docno': docno, 'freq': 1, 'pos': [pos]}]
            #         # term_info[word] = {'uid': term_uid, 'docno': docno, 'frequency': 1, 'position': [pos]}
            #         term_ids[term_uid] = {word}
            #     elif word is in term_info.values():
            #         f
            #     else:                     #if word exists then update the values
            #         term_info[term_uid].append({'docno': docno, 'freq': 1, 'pos': [pos]})
            #         # term_info[term_uid]['docno'].add(docno)
            #         # term_info[term_uid]['freq'] += 1
            #         # term_info[term_uid]['pos'].append(pos)
            #     pos += 1
            #     term_uid += 1
            
            # print(pos)
            # print('doc_num: ', doc_num)
            # print('docno: ', docno)
            
            # print("done")

            # step 3 - build index
print("Done...\n")


def process_commands(**kwargs):
    print(kwargs, '\n')
    
    if 'term' in kwargs and 'doc' in kwargs:
        #--term TERM and --doc DOCNAME6
        input_term = kwargs['term']
        input_doc = kwargs['doc']
        print('--Both term and doc--')
        print('Inverted list for term: ', input_term)
        print('In document: ', input_doc)
        print('TERMID: ', term_ids[input_term])
        print('DOCID: ', doc_ids[input_doc]['doc_uid'])
        print('Term frequency in document: ', )
        print('Positions: ', )
    
    elif 'doc' in kwargs:
        #--doc DOCNAME
        input_doc = kwargs['doc']
        print('--Doc only--')
        print('Listing for document: ', input_doc)
        print('DOCID: ', doc_ids[input_doc]['doc_uid'])
        print('Distinct terms: ', doc_ids[input_doc]['unique_terms'])
        print('Total terms: ', doc_ids[input_doc]['total_terms'])

    elif 'term' in kwargs:
        #--term TERM
        input_term = kwargs['term']
        print('--Term only--')
        print('Listing for term: ', input_term)
        print('TERMID: ', term_ids[input_term])
        print('Number of documents containing term: ', )
        print('Term frequency in corpus: ', )