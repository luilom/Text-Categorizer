import pandas as pd
import logging
logging.basicConfig(level=logging.INFO)
import os
from tqdm import tqdm
from gensim.models.doc2vec import Doc2Vec
from nltk.tokenize import word_tokenize
import re
from sklearn.feature_extraction.text import CountVectorizer
from nltk.stem.snowball import EnglishStemmer


def stemmed_words_count(doc):
	stemmer = EnglishStemmer()
	analyzer = CountVectorizer(stop_words='english').build_analyzer()
	pattern1 = re.compile("(\W+|^)\d+(\W+|$)")
	pattern2 = re.compile("(\W+|^)\d+\s+")
	pattern3 = re.compile("(\W+|^)\d+\Z")
	pattern4 = re.compile("\A\d+(\W+|$)")
	pattern5 = re.compile("\s+\d+(\W+|$)")
	doc = pattern1.sub(" ", doc)
	doc = pattern2.sub(" ", doc)
	doc = pattern3.sub(" ", doc)
	doc = pattern4.sub(" ", doc)
	doc = pattern5.sub(" ", doc)
	return (stemmer.stem(w) for w in analyzer(doc))

def bow_extractor(folder):
    dataset = load_files(folder, encoding='latin1')
	vectorizer = CountVectorizer(decode_error="replace",stop_words='english',analyzer=stemmed_words_count)
	return vectorizer.fit_transform(dataset.data)

def removeDigit(sentence):
        return re.sub("\_\d+", "", sentence)


logging.info("Loading Doc2Vec model")
model3DBOW = Doc2Vec.load("enwiki_dbow/doc2vec.bin")
columns = ["filename","text","vector","label"]
path_dataset_train = 'datasets/datasets_training_test_singole_reti'
datasets = dict()

logging.info("Start with datasets for single NN")
logging.info("First level, all datasets are selected to create dataframes")
for sub_folder in os.listdir(path_dataset_train):
    if os.path.isdir(os.path.join(path_dataset_train,sub_folder)):
        datasets[sub_folder] = os.path.join(path_dataset_train,sub_folder)

logging.info("Starting to create dataframes for any datasets")
for key in tqdm(datasets.keys()):
        bow_dataset = bow_extractor(datasets[key])
        current_dataframe = list()
        for (dirpath, dirnames, filenames) in os.walk(datasets[key]):
                for filename in filenames:
                        current_item = list()
                        current_text = "".join(open(dirpath+"/"+filename).readlines())
                        current_item.append(filename)
                        current_item.append(current_text)
                        current_item.append(model3DBOW.infer_vector(current_text.split()))
                        current_item.append(dirpath.split("/")[len(dirpath.split("/"))-1])
                        current_dataframe.append(current_item)
        pd.DataFrame(current_dataframe, columns = columns).to_pickle("dataframes/single_categories/"+str(key)+".pkl")
        #pd.DataFrame(current_dataframe, columns = columns).to_csv("dataframes/single_categories/"+str(key)+".csv")

logging.info("Start with datasets for Hierarchical structure")

path_dataset_hierarchical_model = 'datasets/datasets_test_modello_gerarchico'


current_dataframe = list()
for (dirpath, dirnames, filenames) in os.walk(path_dataset_hierarchical_model):
        for filename in tqdm(filenames):
                current_item = list()
                current_text = "".join(open(dirpath+"/"+filename).readlines())
                current_item.append(filename)
                current_item.append(current_text)
                current_item.append(model3DBOW.infer_vector(current_text.split()))
                current_item.append(re.sub("\_\d+", "", filename))
                current_dataframe.append(current_item)
pd.DataFrame(current_dataframe, columns = columns).to_pickle("dataframes/hierarchical/hierarchical_model.pkl")
#pd.DataFrame(current_dataframe, columns = columns).to_csv("dataframes/hierarchical/hierarchical_model.csv")






    
