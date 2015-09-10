import flask
from flask import Flask
from flask.ext import restful
from flask.ext.restful import reqparse
from flask import g
import json
from elasticsearch import Elasticsearch
import re
from flask.ext.cors import CORS, cross_origin
import shelve
from os import path
import sys
sys.path.insert(0, '/Volumes/anupam work/review-app-local/scripts/lib/')

import language_functions as text_p

client = Elasticsearch()
SHELVE_DB = 'shelve.db' 

app = Flask(__name__)

#import text_parser as text_p
attribute_seed_file = '/Volumes/anupam work/review-app-local/data/tree-data/percolate_4.json'
hotel_review_id_file = '/Volumes/anupam work/code/showup-code/elastic-search/experiment-reviews/data/tmp/hotel_id_meta.json'

hotel_names_arr = [
    "The Grand Bali Nusa Dua",
    "The Westin Resort Nusa Dua",
    "The Oberoi Bali",
    "The Seminyak Suite Private Villa",
    "All Seasons Legian Bali",
    "Bali Garden Beach Resort",
    "Junjungan Ubud Hotel and Spa",
    "Ungasan Hotel & Convention Center",
    "Balibaliku Beach Front Luxury Private Pool Villa",
    "The Edelweiss Boutique Hotel Kuta",
    "Pradha Villas",
    "Villa Kayu Raja",
    "Alila Ubud",
    "Ize Seminyak",
    "Plataran Ubud Hotel & Spa",
    "Astagina Resort",
    "I-Villa",
    "Aqua Villa",
    "Bali Nusa Dua Hotel",
    "Ion Bali Benoa Hotel",
    "Destiny Boutique Hotel",
    "Alila Villas Soori",
    "Spa Village Resort Tembok Bali",
    "Lembongan Beach Club and Resort",
    "Nusa Dua Retreat and Spa",
    "Tarci Bungalow",
    "B Hotel Bali",
    "Surya Shanti Villa",
    "HARRIS Hotel & Residences Riverview Kuta",
    "Kuta Station Hotel",
    "Amandari",
    "Puri Dajuma Cottages",
    "Bounty Hotel",
    "Hotel NEO + Kuta Legian",
    "Bloo Lagoon Village",
    "Grandmas Seminyak Hotel",
    "Tanah Merah Resort & Gallery",
    "Ivory Resort Seminyak",
    "Champlung Sari Hotel",
    "HARRIS Hotel Bukit Jimbaran",
    "La Joya, Villa & Bungalows",
    "Segara Village Hotel",
    "Mahogany Hotel",
    "The Villas at AYANA Resort",
    "COMO Shambhala Estate",
    "The Grand Sunti",
    "Royal Seminyak: Royal Bali Beach Club",
    "Kupu Kupu Jimbaran & Bamboo Spa by L'Occitane",
    "Sunset Hill",
    "The Griya Villas and Spa",
    "Club Med Bali",
    "Sun Island Hotel Kuta",
    "Swiss-Belresort Watu Jimbar",
    "Chapung SeBali Resort and Spa",
    "Peneeda View Beach Hotel",
    "Mulia Villas",
    "Tulamben Wreck Divers Resort",
    "The Radiant Hotel and Spa",
    "Grand La Villais Hotel",
    "The Layar - Designer Villas and Spa",
    "The Taman Ayu",
    "The Ahimsa Estate",
    "Le Grande Bali",
    "U Paasha Seminyak",
    "Taman Harum Cottages",
    "Puri Wirata Dive Resort and Spa Amed",
    "Puri Saron Seminyak",
    "Nirwana Resort and Spa",
    "Svarga Loka Resort",
    "Amanusa",
    "Semara Luxury Villa Resort",
    "Villa Awang Awang",
    "Swiss-Belinn Seminyak",
    "Shunyata Villas Bali",
    "Golden Tulip Devins Hotel Seminyak",
    "Grand Ixora Kuta Resort",
    "The Sunset Bali Hotel",
    "Solaris Hotel Kuta",
    "Sun Royal Hotel",
    "Indiana Kenanga Villas",
    "Bunga Permai Hotel",
    "The Menjangan",
    "The Segara Suites",
    "Amaroossa Suite Bali",
    "Centra Taum Seminyak Bali",
    "Ananta Legian Hotel",
    "Kayumanis Jimbaran Private Estate & Spa",
    "Agung Raka Resort & Villas",
    "The Open House",
    "PING Hotel Seminyak Bali",
    "Grand Balisani Suites",
    "The Alea Hotel Seminyak",
    "The Niche Bali",
    "Keraton Jimbaran Resort & Spa",
    "Bliss Surfer Hotel",
    "The Sanyas Suite Seminyak",
    "The Tusita Hotel",
    "Sense Hotel Seminyak",
    "Hotel Horison Seminyak",
    "The Lovina",
    "The Vira Bali Hotel",
    "Bhavana Private Villas",
    "Kuta Puri Bungalows",
    "Hotel Tjampuhan & Spa",
    "Biyukukung Suites and Spa",
    "Batu Karang Lembongan Resort & Day Spa",
    "The Club Villas",
    "Bebek Tepi Sawah Villas & Spa",
    "Santi Mandala",
    "Tegal Sari",
    "Holiday Inn Express Bali Raya Kuta",
    "FuramaXclusive Ocean Beach",
    "Liberty Dive Resort",
    "Royal Candidasa: Royal Bali Beach Club",
    "100 Sunset 2 Hotel",
    "H Sovereign Bali",
    "BEST WESTERN PREMIER Sunset Road Kuta",
    "Dewi Sri Hotel",
    "Bali Niksoma Boutique Beach Resort",
    "Villa Air Bali Boutique Resort & Spa",
    "Grand Istana Rama Hotel Bali",
    "Mercure Resort Sanur",
    "Villa Sarna Ubud",
    "Artemis Villa and Hotel",
    "Mega Boutique Hotel",
    "Hu'u Villas Bali",
    "Fivelements Puri Ahimsa",
    "Hotel Vila Lumbung",
    "The Akmani Legian",
    "Legian Paradiso Hotel",
    "The Purist Villas and Spa",
    "Saren Indah Hotel",
    "Kind Villa Bintang Resort & Spa",
    "Ibis Styles Bali Kuta Legian",
    "Nandini Bali Resort & Spa Ubud",
    "WakaGangga",
    "Love F Hotel",
    "The Mansion Resort Hotel & Spa",
    "Patra Jasa Bali Resort & Villas",
    "Bambu Indah",
    "Candi Beach Cottage",
    "Maya Loka Villas",
    "Alam KulKul Boutique Resort",
    "Villa Kresna",
    "Poinciana Oceanside Resort & Retreat Centre",
    "The 101 Legian",
    "kaMAYA Resort and Villas",
    "Pelangi Bali Hotel",
    "Harper Kuta",
    "Ibis Bali Kuta",
    "Disini Luxury Spa Villas",
    "Rijasa Agung - Bali Ubud Luxury Hotel Resort Villa",
    "Puri Sunia Resort",
    "Maharani Beach Hotel",
    "Ibis Styles Bali Kuta Circle",
    "Sun Island Hotel Legian",
    "Komune Resort, Keramas Beach Bali",
    "Belmond Jimbaran Puri",
    "Villa Karisa",
    "HARRIS Resort Kuta Beach",
    "The One Villa",
    "Alila Manggis",
    "Le Jardin Villas",
    "Hotel Tugu Bali",
    "The Dipan Resort Petitenget",
    "Ulu Segara Luxury Suites & Villas",
    "Ibis Styles Bali Benoa",
    "The Gangsa Private Villa by Kayumanis",
    "Legian Beach Hotel",
    "The Mulia",
    "Puri Wulandari Boutique Resort",
    "Alindra Villa",
    "Matahari Tulamben Resort, Dive & SPA",
    "The Sungu Resort & Spa",
    "Amankila",
    "Peppers Seminyak",
    "Hotel Santika Siligita Nusa Dua",
    "EDEN Hotel Kuta Bali - Managed by Tauzia",
    "Ramada Resort Camakila Bali",
    "Alam Puri Art Museum & Resort",
    "Zen Resort Bali",
    "Karma Jimbaran",
    "Puri Sebali Resort",
    "Harris Hotel Seminyak",
    "The Payogan Villa Resort & Spa",
    "18 Suite Villa Loft",
    "The Bene Hotel",
    "The Royal Eighteen Resort and Spa",
    "Natura Resort and Spa",
    "Mara River Safari Lodge",
    "Mantra Sakala Resort & Beach Club, Bali",
    "The Haven Seminyak Hotel & Suites",
    "Nefatari Exclusive Villas",
    "Sun Island Villas & Spa",
    "Puri Gangga Resort",
    "Seaside Suites Bali",
    "The Ulin Villas & Spa",
    "Satriya Cottages",
    "Mercure Bali Legian",
    "Villa Kubu",
    "Bali Shangrila Beach Club",
    "The Breezes Bali Resort & Spa",
    "Sun Boutique Hotel Managed by BENCOOLEN",
    "Griya Santrian",
    "Kenanga Boutique Hotel",
    "Mercure Bali Nusa Dua",
    "Kejora Suites",
    "Sri Ratih Cottages",
    "Double-Six Luxury Hotel Seminyak",
    "The Jineng Villas",
    "Bali Mandira Beach Resort & Spa",
    "Park Regis Kuta Bali",
    "The Bale",
    "Swiss-Belinn Legian",
    "Amana Villas",
    "The Puri Nusa Dua",
    "Puri Santrian",
    "Bintang Kuta Hotel",
    "White Rose Hotel & Villas",
    "Anantara Bali Uluwatu Resort & Spa Bali",
    "The Elysian",
    "Grand Whiz Hotel Nusa Dua",
    "The Legian Bali, a GHM hotel",
    "Bali Ginger Suites",
    "Bali Island Villas & Spa",
    "The Laguna, a Luxury Collection Resort & Spa",
    "Furama Villas & Spa Ubud",
    "Sudamala Suites & Villas",
    "The Ritz-Carlton, Bali",
    "Vasanti Seminyak Resort",
    "Alaya Resort Ubud",
    "Blue Karma Hotel",
    "BEST WESTERN Kuta Beach",
    "Dusun Villas Bali",
    "Kuta Angel Hotel",
    "Maca Villas & Spa",
    "The Amala",
    "Ossotel",
    "The Chedi Club Tanah Gajah, Ubud, Bali, a GHM hotel",
    "Villa Seminyak Estate & Spa",
    "Royal Jimbaran: Royal Bali Beach Club",
    "Aria Villas Ubud",
    "Mutiara Bali Boutique Resort & Villas",
    "Anantara Seminyak Resort & Spa, Bali",
    "Ubud Bungalow",
    "Abi Bali Resort & Villa",
    "Swiss-Belhotel Segara Resort & Spa",
    "Aston Kuta Hotel & Residence",
    "Pita Maha Resort and Spa",
    "The Kayana Bali",
    "The Magani Hotel and Spa",
    "Hotel Terrace At Kuta",
    "L Hotel Seminyak",
    "Kayumanis Ubud Private Villa & Spa",
    "Awarta Nusa Dua Luxury Villas & Spa",
    "Gending Kedis Villas & Spa Estate",
    "Holiday Inn Express Bali Kuta Square",
    "Damai",
    "Jamahal Private Resort & SPA",
    "Citadines Kuta Beach Bali",
    "Swiss-Belhotel Rainforest",
    "Villa Semana",
    "Mercure Kuta Bali",
    "Bali Tropic Resort and Spa",
    "The Trans Resort Bali",
    "Grand Inna Kuta",
    "The Ubud Village Resort & Spa",
    "The Royal Pita Maha",
    "Karma Kandara",
    "Mulia Resort",
    "Prama Sanur Beach Bali",
    "The Kana Kuta",
    "Sol Beach House Benoa Bali by Melia Hotel International",
    "Alila Villas Uluwatu",
    "Ramada Encore Bali Seminyak",
    "The Villas Bali Hotel & Spa",
    "Tanadewa Luxury Villas & Spa",
    "Kuta Central Park Hotel",
    "Le Meridien Bali Jimbaran",
    "KajaNe Mua Private Villa & Mansion",
    "Samabe Bali Suites & Villas",
    "Courtyard by Marriott Bali Seminyak",
    "Risata Bali Resort & Spa",
    "Four Seasons Resort Bali at Sayan",
    "Luna2 Studiotel",
    "Fairmont Sanur Beach Bali",
    "The St. Regis Bali Resort",
    "Padma Resort Legian",
    "Ramada Bintang Bali Resort",
    "The Samaya Bali",
    "Grand Mirage Resort",
    "Sheraton Bali Kuta Resort",
    "Kupu Kupu Barong Villas and Tree Spa",
    "Rama Candidasa Resort & Spa",
    "Komaneka at Monkey Forest",
    "Novotel Bali Benoa",
    "Fontana Hotel Bali",
    "Four Seasons Resort Bali at Jimbaran Bay",
    "Komaneka at Bisma",
    "Wapa di Ume Resort and Spa",
    "Grand Aston Bali Beach Resort",
    "Ayung Resort Ubud",
    "Grand Hyatt Bali",
    "The Kayon Resort",
    "The Seminyak Beach Resort & Spa",
    "Atanaya Hotel",
    "The Stones Hotel - Legian Bali, Autograph Collection",
    "Bulgari Resort Bali",
    "Ramayana Resort & Spa",
    "Uma by COMO, Ubud",
    "Hard Rock Hotel Bali",
    "Conrad Bali",
    "Kamandalu Ubud",
    "Banyan Tree Ungasan, Bali",
    "The Kunja Villas & Spa",
    "RIMBA Jimbaran Bali by AYANA",
    "Pullman Bali Legian Nirwana",
    "Viceroy Bali",
    "Sofitel Bali Nusa Dua Beach Resort",
    "Kuta Seaview Boutique Resort & Spa",
    "Komaneka at Rasa Sayang",
    "Discovery Kartika Plaza Hotel",
    "Kuta Paradiso Hotel",
    "Maya Ubud Resort & Spa",
    "Amori Villas",
    "Kayumanis Nusa Dua Private Villa & Spa",
    "Amadea Resort & Villas",
    "Nusa Dua Beach Hotel & Spa",
    "Melia Bali Indonesia",
    "The Kuta Beach Heritage Hotel Bali - Managed by Accor",
    "Amarterra Villas Bali Nusa Dua - MGallery Collection",
    "BEST WESTERN Kuta Villa",
    "Pan Pacific Nirwana Bali Resort",
    "Uma Sapna",
    "Uppala Villa Seminyak",
    "Grand Nikko Bali"
]

#def load_everything():
#    text_parser_loaded = getattr(g, 'text_parser_loaded', None)
##    if 'text_parser_loaded' in db:
##        text_parser_loaded = db['text_parser_loaded']
##    else:
##        text_parser_loaded = None
#    print 'text_parser_loaded: ' + str(text_parser_loaded)
#    
#    attr_seed = getattr(g, 'attribute_seed', None)
#    #print 'seed: ' + str(attr_seed)
#    
#    if attr_seed == None:
#        attr_seed = json.loads(open(attribute_seed_file, 'r').read())
#        setattr(g, 'attribute_seed', attr_seed)
#    
#    #print 'text_parser_loaded: ' + str(text_parser_loaded)
#    if text_parser_loaded == None:
#        text_p.load_model_files()
#        print 'setting text_parser_loaded: ' + str(True)
#        setattr(g, 'text_parser_loaded', True)
#        #db['text_parser_loaded'] = True
#        #session['text_parser_loaded'] = True
#        #text_parser_loaded = db['text_parser_loaded']
#        val = getattr(g, 'text_parser_loaded')
#        print 'text_parser_loaded immediate: ' + str(val)
#        
#    return attr_seed
#        
#def load_hotel_review_data():
#    match_data = getattr(g, 'hotel_review_id', None)
#    if match_data == None:
#        match_data = json.loads(open(hotel_review_id_file, 'r').read())
#    return match_data

a = reqparse.RequestParser()
a.add_argument('search_str', type=str)
 
def convert_to_hotel_review_id_resuts(response, match_data, attr):
    result = {}
    for item in response['hits']['hits']:
        hotel_id = str(item['_source']['hotel_id'])
        review_id = str(item['_source']['review_id'])
        line_no = item['_source']['attribute_line'][attr]
        if review_id not in match_data[hotel_id]:
            print 'not present: ' + str(hotel_id) + ' ; ' + str(review_id)
            continue
        review_obj = match_data[hotel_id][review_id]
        #print json.dumps(review_obj)
        review_arr = re.split('\.|\?| !', ''.join(review_obj['description']))
        length = len(review_arr)
        if length <= line_no:
            print 'not in index: ' + str(review_obj['description'])
            print 'line: ' + str(line_no) + str(len(review_obj['description']))
            continue
        review_line = review_arr[line_no]
        if hotel_id not in result:
            result[hotel_id] = {}
        result[hotel_id][review_id] = review_line
    return result
    
def convert_to_hotel_review_id_images(response):
    result = {}
    for item in response['hits']['hits']:
        hotel_id = str(item['_source']['hotel_id'])
        url = str(item['_source']['url'])
        if hotel_id not in result:
            result[hotel_id] = []
        result[hotel_id].append(url)
    return result
    
class HelloHandler(restful.Resource):
    '''
    1. Text parser for the argument.
    2. elastic search in the image index.
    3. elastic search in the review search.
    4. parsing of both results.
    5. combining of results.
    6. returning the json.
    
    '''
    attr_seed = None
    match_data = None
    def __init__(self):
        print 'init init'
        self.attr_seed = json.loads(open(attribute_seed_file, 'r').read())
        self.match_data = json.loads(open(hotel_review_id_file, 'r').read())
        text_p.load_model_files()
        print 'end init'
    
    def get(self):
        args = a.parse_args()
        search_criteria = args.get('search_str')
        print 'search_criteria: ' + search_criteria
        print 'in get'
        #attr_seed = load_everything()
        assert(self.attr_seed != None)
        assert(text_p.is_model_loaded())
        print 'before match_data'
        #match_data = load_hotel_review_data()
        print 'after match_data'
        path = text_p.find_attribute_2(self.attr_seed, search_criteria)
        
        print ("path: " + str(path))
        attr = path[len(path) - 1][0]
        #attr = "pool"
        
        response_images = client.search(
            index="hn",
            size=10000,
            body={
                "query": {
                    "nested": {
                        "path": "attributes",
                        "query": {
                            "bool": {
                                "must": [
                                    { "match": {"attributes.value": attr}}
                                ]
                            }
                        }
                    }
                }
            }
        )
        
        result_images = convert_to_hotel_review_id_images(response_images)
        
        #print 'images: ' + str(result_images)
        
        response_reviews = client.search(
            index="hn_reviews",
            size=10000,
            pretty=True,
            body={
                "query": {
                    "nested": {
                        "path": "attribute_list",
                        "query": {
                            "bool": {
                                "must": [
                                    { "match": {"attribute_list.value": attr}}
                                ]
                            }
                        }
                    }
                }
            }
        )
        
        assert(self.match_data != None)
        results_reviews = convert_to_hotel_review_id_resuts(response_reviews, self.match_data, attr)
        
        #print 'reviews: ' + str(results_reviews)
        
        mixed = []
        count = 0
        for hotel_id in result_images:
            obj = {}
            obj['hotel_id'] = hotel_id
            obj['hotel_name'] = hotel_names_arr[count]
            obj['attribute'] = attr
            if len(result_images[hotel_id]) < 2:
                print 'too few images for hotel_id: ' + str(hotel_id)
                continue
            obj['cover_image'] = result_images[hotel_id][0]
            obj['images'] = result_images[hotel_id][1:]
            if hotel_id in results_reviews:
                review_arr = []
                for review_id in results_reviews[hotel_id]:
                    review_obj = {}
                    review_obj['review'] = results_reviews[hotel_id][review_id]
                    review_obj['user'] = {"name":  "Amit Brah", "avatr" : "https://s3.amazonaws.com/uifaces/faces/twitter/sauro/128.jpg"}
                    review_arr.append(review_obj)
                obj['reviews'] = review_arr
            else:
                obj['reviews'] = []
                print 'No reviews found for hotel id: ' + str(hotel_id)
                continue
            obj['address'] = 'Jalan Nakula No. 18, Seminyak, Bali 80361, Indonesia'
            mixed.append(obj)
            count += 1
        
        print 'returning...'
        return mixed, 200
        #return path[len(path) - 1], 200

    
if __name__ == '__main__':
    cors = CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type' 
    api = restful.Api(app)
    api.add_resource(HelloHandler, '/hello')
    app.run(debug=True,  port = 8012, host="0.0.0.0")