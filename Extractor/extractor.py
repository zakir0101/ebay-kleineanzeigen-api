import json
from bs4 import BeautifulSoup, Tag



class EbayKleinanzeigenExtractor:
    def __init__(self, soup: Tag, path: str = "/"):
        self.soup = soup
        self.path = ""

    def parse(self, path, filename):
        self.path = path

        f = open(self.path + filename)
        desc: dict = json.load(f)
        res = dict()
        if desc.get('type'):
            if "parent_list" in desc.get("type"):
                return self.read_items(self.soup, desc)

        for item_title, item_desc in desc.items():

            if 'parent_list' in item_desc['type']:

                res[item_title] = self.read_items(self.soup, item_desc)
            else:
                res[item_title] = self.read_item(self.soup, item_desc)

        return res

    ####################################################
    #                 get item
    ####################################################

    def read_item(self, elm: Tag, desc):
        res = ""

        if desc['type'] == 'text':
            temp = self.find(elm, desc)
            if temp:
                res = temp.text
                if desc.get("split"):
                    res = res.split(desc.get("splitter"))[desc.get('index')]
                if desc.get("strip"):
                    res = res.strip()
                if desc.get('rm_newline'):
                    res = res.replace("\n","")
                if desc.get('rm_space'):
                    res = " ".join(res.split())

                return res
            else:

                return ""

        elif desc['type'] == 'link':
            temp = self.find(elm, desc)
            if temp:
                res = temp["href"]
                if desc.get('category_code'):
                    res = res[res.rindex("/") + 1:]
                return res
            else:
                return ""

        elif desc['type'] == 'image':
            temp = self.find(elm, desc)
            if temp:
                res = temp["src"]
                return res
            else:
                return ""

        elif desc['type'] == 'attr':
            temp = self.find(elm, desc)
            if temp:
                attr = desc['attr']
                if temp.has_attr(attr):
                    res = temp[attr]
                    return res
                else:
                    return ""
            else:
                return ""


        elif desc['type'] == 'parent':
            temp = self.find(elm, desc)
            if temp:
                elm = temp
                return self.read_item(elm, desc['children'])
            else:
                return ""

        else:
            return ""

    ####################################################
    #                 get items
    ####################################################
    def read_items(self, elm: Tag, parent_desc):
        res = []
        children = {}
        number = 1
        parent: Tag

        if parent_desc.get("number"):
            number = parent_desc['number']
        if "file" in parent_desc['type']:
            children = json.load(open(self.path + parent_desc['filename']))
        else:
            children = parent_desc.get('children')

        if parent_desc['element'] == "None":
            parent = elm
        else:
            parent = self.find(elm, parent_desc)

        if not parent:
            return res

        children_elms = self.find_children(parent, desc=parent_desc, all=True,
                                           recursive=parent_desc.get('recursive') or True)
        if parent_desc['type'] == "parent_list_count":
            return len(children_elms)

        if len(children_elms) == 0:
            return res

        for elm in children_elms:
            child = {}
            for child_title, child_desc in children.items():
                if 'parent_list' in child_desc['type']:
                    child[child_title] = self.read_items(elm, child_desc)
                else:
                    child[child_title] = self.read_item(elm, child_desc)

            res.append(child)

        if "single" in parent_desc['type']:
            if len(res) >= number:
                return res[number-1]
            else:
                return None

        return res

    ####################################################
    #                 find children
    ####################################################

    def find_children(self, elm: Tag, desc, all=False, recursive=True):
        child_desc = dict()
        child_desc['type'] = "unknown"
        child_desc['element'] = desc['child_element']
        child_desc['class'] = desc.get('child_class')
        child_desc['id'] = desc.get('child_id')
        return self.find(elm, child_desc, all=all, recursive=recursive)

    ####################################################
    #                 find Element
    ####################################################

    def find(self, elm: Tag, desc, all=False, recursive=True):
        tage_name: str = desc.get('element')
        number: int = 1
        match desc.get('type'):
            case "link":
                tag_name = desc.get('element') or 'a'
            case 'image':
                tag_name = desc.get('element') or 'img'
            case _:
                tag_name = desc.get('element')

        if desc.get('number'):
            number = desc['number']
        class_ = desc.get('class')
        id = desc.get('id')
        res = ""
        if class_ and id:
            res = elm.find_all(tag_name, class_=class_, id=id, recursive=recursive)
            if res and not all:
                res = self.get_element_from_list(res, number)
        elif class_ and not id:
            res = elm.find_all(tag_name, class_=class_, recursive=recursive)
            if res and not all:
                res = self.get_element_from_list(res, number)

        elif not class_ and id:
            res = elm.find_all(tag_name, id=id, recursive=recursive)
            if res and not all:
                res = self.get_element_from_list(res, number)


        elif not class_ and not id:
            res = elm.find_all(tag_name, recursive=recursive)
            if res and not all:
                res = self.get_element_from_list(res, number)

        if res:
            if desc.get("print"):
                print("tag = ",tage_name, ", class= ", class_, ", id= ", id, " was  Found :)")

        else:
            if desc.get("print"):
                print("tag = ",tage_name, ", class= ", class_, ", id= ", id, " was not Found :(")

        return res

    def get_element_from_list(self, elm_list, number):
        if len(elm_list) < number:
            return None
        return elm_list[number - 1]
