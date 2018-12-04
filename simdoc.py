import plac
import io
import spacy
nlp = spacy.load('en_core_web_lg')

def main(textloc1, textloc2):

	with io.open(textloc1, 'r', encoding='utf8') as file1_:
	   text1 = file1_.read()
	
	with io.open(textloc2, 'r', encoding='utf8') as file2_:
	   text2 = file2_.read()

	text1tokens = nlp(text1)
	text2tokens = nlp(text2)
	
	print(text1tokens.similarity(text2tokens))
         
if __name__ == '__main__':
    plac.call(main)
    