from pathlib import Path
import shutil
import sys

IMAGES = ('JPEG', 'PNG', 'JPG', 'SVG', 'BMP')
VIDEOS = ('AVI', 'MP4', 'MOV', 'MKV')
DOCS = ('DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX')
MUSIC = ('MP3', 'OGG', 'WAV', 'AMR')
ARCHIVES = ('ZIP', 'GZ', 'TAR')
APPS = ('EXE','APK')

CATEGORIES = {'images': ['JPEG', 'PNG', 'JPG', 'SVG', 'BMP'],
              'videos': ['AVI', 'MP4', 'MOV', 'MKV'],
              'docs': ['DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'],
              'music': ['MP3', 'OGG', 'WAV', 'AMR', 'AIFF'],
              'archives': ['ZIP', 'GZ', 'TAR'],
              'apps': ['EXE','APK'] }  

found_files = {'images': [],
              'videos': [],
              'docs': [],
              'music': [],
              'archives': [],
              'apps': [] }

CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
            "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")
CYR = list(CYRILLIC_SYMBOLS)
TRANS = {}

for c, l in zip(CYR, TRANSLATION):    
    TRANS[ord(c)] = l
    TRANS[ord(c.upper())] = l.upper()    

images = []
videos = []
docs = []
music = []
archives = []
apps = []
others = []
known_types = []
unknown_types = []

def normalize(file_name:str) -> str:
    output = ""
       
    for ch in file_name:
        if ch.lower() in CYR:
            output += ch.translate(TRANS)
        elif  ch.isnumeric() or ch.isalpha() or ch == "." or ch == " ":
            output += ch
        else:
            output += "_"
            
    return output


def scan_folder(path:Path):
    
    contents = [x for x in path.iterdir()]
    for item in contents:
        
        if item.is_file():
            ext = item.suffix[1:].upper()
            
        
            for name, types in CATEGORIES.items():
                if ext in types: 
                    found_files[name].append(item)
                    known_types.append(ext)
                else:
                    unknown_types.append(ext)
            
            
            # if ext in IMAGES:
            #     images.append(item)
            #     known_types.append(ext)
            # elif ext in VIDEOS:
            #     videos.append(item)  
            #     known_types.append(ext)
            # elif ext in DOCS:
            #     docs.append(item)    
            #     known_types.append(ext)
            # elif ext in MUSIC:
            #     music.append(item)    
            #     known_types.append(ext)
            # elif ext in ARCHIVES:
            #     archives.append(item)
            #     known_types.append(ext)
            # elif ext in APPS:
            #     apps.append(item)
            #     known_types.append(ext)
            # else:
            #     others.append(item)   
            #     unknown_types.append(ext)

        else:
            if item.name not in CATEGORIES.keys():
                scan_folder(item)
            else: 
                continue


def move_files(files_list:list, target_path:Path, new_folder_name:str) -> list:
    output_list = []
    new_dir = target_path / new_folder_name
    try:
        new_dir.mkdir()
    except FileExistsError:
        pass
    for file in files_list:
        new_name = normalize(file.name)
        output_list.append(new_name)
        try:
            file.rename(f'{new_dir}\{new_name}')
        except FileExistsError:
            file.unlink() #delete doubles
    return output_list
 
        
def unpack_files(files_list:list, target_path:Path) -> list:
    output_list = []
    arc_dir = target_path / 'archives'
    try:
        arc_dir.mkdir()
    except FileExistsError:
        pass
    for file in files_list:
        new_name = normalize(file.name).split('.')[0]
        new_dir = arc_dir / new_name
        new_dir.mkdir()
        shutil.unpack_archive(file, new_dir)
        output_list.append(normalize(file.name))
        file.unlink() #delete unpacked archive
        
    return output_list


def del_empty_folders(path):
    folders = [x for x in path.iterdir() if x.is_dir()]
    for item in folders:
        if item.name not in CATEGORIES.keys():
            if len(list(Path(item).iterdir())) == 0:
                item.rmdir()
            else:
                del_empty_folders(item)
        else:
            continue        

            
def normalize_all(path):
    items = [x for x in path.iterdir()]
    for item in items:
        if item.is_file():
            new_name = item.parent / normalize(item.name)
            item.rename(new_name)
        else:
            if item.name not in CATEGORIES.keys():
                new_name = item.parent / normalize(item.name)
                item.rename(new_name)
                normalize_all(item)
            else: 
                continue    

def report_category(category:str, files_lst: list):
    print(f'Found files in category "{category}": ', len(files_lst))
    for file in files_lst:   
        print(file)  


def main():
    # work_path = sys.argv[1]
    work_path = r'E:\unsorted'
    path = Path(work_path)
    scan_folder(path)
    found_known = set(known_types)
    found_unknown = set(unknown_types)
    
    # create folders only for found file types
    
    for category in found_files.keys():
        
        if category == 'archives':
            if len(found_files.get(category)) > 0:
                report_category(category, unpack_files(archives, path))
            
        if len(found_files.get(category)) > 0:
            report_category(category, move_files(found_files.get(category), path, str(category)))
        
        
    
    # if music:
    #     music_report = move_files(music, path, 'music')
    #     report_category('Music', music_report)
    
    # if images:
    #     images_report = move_files(images, path, 'images')
    #     report_category('Images', images_report)
    
    # if videos:
    #     videos_report = move_files(videos, path, 'videos')
    #     report_category('Videos', videos_report)
        
    # if docs:
    #     docs_report = move_files(docs, path, 'docs')
    #     report_category('Docs', docs_report)
    
    # if apps:
    #     apps_report = move_files(apps, path, 'apps')
    #     report_category('Apps', apps_report)
        
      
    
    del_empty_folders(path)
    
    normalize_all(path)
       
    
    print('Found known file types:', ", ".join(f for f in found_known))
    print('Found unknown file types:', ", ".join(f for f in found_unknown))
    
    
    
if __name__ == '__main__':
    main()


