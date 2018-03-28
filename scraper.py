from bs4 import BeautifulSoup
from requests import get
import datetime
import pandas as pd

class WebScraper():
    
    NO_DATA_FROM_REMOTE_ERROR = 'No data received from remote source'
    NO_RESPONSE_FROM_REMOTE_ERROR = 'No response received from remote source'

    def __init__(self, baseurl, variable, container_tag, container_class, attribute_tags, value_name, attribute_class):
        self.baseurl = baseurl
        self.variable = datetime.datetime.strptime(variable, '%Y-%m-%d').date()
        self.container_tag = container_tag
        self.container_class = container_class
        self.attribute_tags = attribute_tags
        self.value_name = value_name
        self.attribute_class = attribute_class

    def createseq(self, num):
        var_list = [self.variable + datetime.timedelta(i) for i in range(num)]
        return var_list

    def soupParser(self, soup):
        if self.container_class:
            data_container = soup.find_all(self.container_tag, class_=self.container_class)
        else:
            data_container = soup.find_all(self.container_tag)
        attributes = {}
        for i in range(len(data_container)):
            attributes[i] = {}
            for tag, name, class_ in zip(self.attribute_tags, self.value_name, self.attribute_class):
                if class_:
                    curr_element = data_container[i].find(
                        tag, class_=class_)
                else:
                    curr_element = data_container[i].find(tag)
                if curr_element:
                    attributes[i][name] = curr_element.contents[0].strip()
        return attributes

    def storeData(self, data_dict):
        data_df = pd.DataFrame.from_dict(data_dict, orient='index')
        return data_df
            
    def scrape(self, num):
        var_list = self.createseq(num)
        for curr_var in var_list:
            curr_url = self.baseurl + str(curr_var)
            try:
                respose = get(curr_url)
                if respose:
                    websoup = BeautifulSoup(respose.text, 'html.parser')
                    data = self.soupParser(websoup)
                else:
                    raise Exception(self.NO_RESPONSE_FROM_REMOTE_ERROR)
                if data:
                    data_df = self.storeData(data)
                    return data_df
                else:
                    raise Exception(self.NO_DATA_FROM_REMOTE_ERROR)
            
            except Exception as e:
                if e == Exception(self.NO_RESPONSE_FROM_REMOTE_ERROR):
                    raise Exception(self.NO_RESPONSE_FROM_REMOTE_ERROR)
                elif e == Exception(self.NO_DATA_FROM_REMOTE_ERROR):
                    raise Exception(self.NO_DATA_FROM_REMOTE_ERROR)
                else:
                    raise e


'''def main():
    ws = WebScraper('https://spotifycharts.com/regional/us/daily/'
                    , '2018-02-01'
                    , 'tr'
                    , None
                    , ['strong', 'span', 'td']
                    , ['Track Name', 'Artist', 'Streams']
                    , [None, None, 'chart-table-streams'])
    print(ws.scrape(1).head())

if __name__ == '__main__':
    main()'''
