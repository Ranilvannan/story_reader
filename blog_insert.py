import os
import json


class BlogInsert:

    def __init__(self, path, col, params, file_suffix):
        self.path = path
        self.col = col
        self.params = params
        self.file_suffix = file_suffix

    def trigger_import(self):
        files = self.get_json_files()

        for file in files:
            insert_list, update_list = self.get_json_data(file)
            self.bulk_insert(insert_list)
            self.update_blog(update_list)

            if os.path.exists(file):
                os.remove(file)

    def bulk_insert(self, recs):
        if recs:
            self.col.insert_many(recs)

    def update_blog(self, recs):
        for rec in recs:
            # data_dict = {"story_id": rec["story_id"]}
            data_dict = {self.params: rec[self.params]}
            self.col.find_one_and_replace(data_dict, rec)

    def get_json_data(self, file):
        insert_list = []
        update_list = []

        with open(file) as json_file:
            recs = json.load(json_file)
            if isinstance(recs, list):
                for rec in recs:
                    data_dict = {self.params: rec[self.params]}
                    res = self.col.find(data_dict).count()
                    if res:
                        update_list.append(rec)
                    else:
                        insert_list.append(rec)

        return insert_list, update_list

    def get_json_files(self):
        list_files = os.listdir(self.path)
        json_list = []

        for item in list_files:
            if item.endswith(self.file_suffix):
                file_path = os.path.join(self.path, item)
                json_list.append(file_path)

        return json_list
