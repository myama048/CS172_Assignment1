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
token_regex = re.compile("\w+([\,\.]\w+)*")
#apply stemming to tokens
porter = PorterStemmer()

#zip extract function, uncomment out later
with zipfile.ZipFile("ap89_collection_small.zip", 'r') as zip_ref:
    zip_ref.extractall()

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

            #---------
            #remove all punctuations
            # text = text.translate(str.maketrans('', '', string.punctuation))
            #tokenize the text
            # text_tokens = word_tokenize(text)
            #remove all stopwords from stopwords.txt file
            # text_tokens_without_sw = [word for word in text_tokens if word not in stopwords]
            #---------

            text_tokens = []
            for match in re.finditer(token_regex, text):
                token = (match.group())
                # Remove apostrophe
                token = token.split("'")[0]
                if (token in stopwords):
                    continue
                # Add the token to our list
                text_tokens.append(token)


            #create a unique_terms set to keep count of unique words
            unique_terms = set()
            text_stemmed_sw = []
            #----------------
            # for word in text_tokens_without_sw:
            #     unique_terms.add(word)
            #     text_stemmed_sw.append(porter.stem(word))
            #----------------
            for word in text_tokens:
                stemmed = porter.stem(word)
                text_stemmed_sw.append(stemmed)
                unique_terms.add(stemmed)



            # step 2 - create tokens
            pos = 1
            #add new doc entry 
            doc_ids[docno] = {'doc_uid': doc_uid, 'total_terms': len(text_stemmed_sw), 'unique_terms': len(unique_terms)}

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

            doc_uid += 1

            # step 3 - build index
print("Done...\n")



def count_term(term, method_check, doc_name=''):

    if method_check == "doc_contain_term": #used in --term
        return(len(term_info[term]))
    
    if method_check == "freq_corpus": #used in --term
        total = 0
        for value in term_info[term]:
            total += value['freq']
        return(total)

    if method_check == "freq_doc": #used in --term --doc
        for value in term_info[term]:
            if value['docno'] == doc_name:
                return(value['freq'])

    if method_check == "pos": #used in --term --doc
        for value in term_info[term]:
            if value['docno'] == doc_name:
                return(value['pos'])


def process_commands(**kwargs):
    # print(kwargs, '\n')
    
    if 'term' in kwargs and 'doc' in kwargs:
        #--term TERM and --doc DOCNAME6
        input_term = porter.stem(kwargs['term'])
        input_doc = kwargs['doc'].upper()
        print('--Both term and doc--')
        print('Inverted list for term: ', kwargs['term'])
        print('In document: ', input_doc)
        print('TERMID: ', term_ids[input_term])
        print('DOCID: ', doc_ids[input_doc]['doc_uid'])
        print('Term frequency in document: ', count_term(input_term, 'freq_doc', input_doc))
        print('Positions: ', count_term(input_term, 'pos', input_doc))
    
    elif 'doc' in kwargs:
        #--doc DOCNAME
        input_doc = kwargs['doc'].upper()
        print('--Doc only--')
        print('Listing for document: ', input_doc)
        print('DOCID: ', doc_ids[input_doc]['doc_uid'])
        print('Distinct terms: ', doc_ids[input_doc]['unique_terms'])
        print('Total terms: ', doc_ids[input_doc]['total_terms'])

    elif 'term' in kwargs:
        #--term TERM
        input_term = porter.stem(kwargs['term'])
        print('--Term only--')
        print('Listing for term: ', kwargs['term'])
        print('TERMID: ', term_ids[input_term])
        print('Number of documents containing term: ', count_term(input_term, "doc_contain_term"))
        print('Term frequency in corpus: ', count_term(input_term, "freq_corpus"))


#creates term_index.txt file and writes to it
f_term_index = open("term_index.txt", mode='w', encoding='utf-8') 
for key, value in term_info.items():
    # print(term_ids[key])
    f_term_index.write(str(term_ids[key]) + '\t')
    for value in term_info[key]:
        # f_term_index.write(str(value['docno']) + ':')
        # print(value['docno'],':')
        for pos in value['pos']:
            # print(value['docno'])
            # print(pos)
            f_term_index.write(str(value['docno']) + ':' + str(pos) + '\t')
    f_term_index.write('\n')
f_term_index.close()


#creates term_info.txt file and writes to it
f_term_info = open("term_info.txt", mode='w', encoding='utf-8') 
for key, value in term_info.items():
    write_freq = count_term(key, 'freq_corpus')
    write_doc = count_term(key, 'doc_contain_term')
    f_term_info.write(str(term_ids[key]) + '\t' + str(write_freq) + '\t' + str(write_doc) + '\n')
f_term_info.close()


#creates docids.txt file and writes to it
f_docids = open("docids.txt", mode='w', encoding='utf-8') 
for key, value in doc_ids.items():
    f_docids.write(str(value['doc_uid']) + '\t' + str(key) + '\n')
f_docids.close()

#creates termids.txt file and writes to it
f_termids = open("termids.txt", mode='w', encoding='utf-8') 
for key, value in term_ids.items():
    f_termids.write(str(value) + '\t'+ str(key) + '\n')
f_termids.close()