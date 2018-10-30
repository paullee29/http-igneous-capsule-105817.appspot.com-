
# Functions to prepare laymans text for HTML tagging

def openraw (filename): 
    input_html = open (filename , 'r')
    raw_html = ""
    for line in input_html:
        raw_html = raw_html + line
    return raw_html


def linkify (Text): # Goes through Text and turns Link text into HTML Lists
    while Text.find('(LINK:(') > -1:
        start_location = Text.find('(LINK:(')
        end_location = Text.find(')', start_location+1)
        name_start_location = Text.find(", ", start_location)
        name_end_location = Text.find(")",name_start_location+1)
        Link = '<a target ="_blank" href = "'+Text[start_location+7:end_location]+'">'+Text[name_start_location+2:name_end_location]+'</a>'
        Text = Text[:start_location] + Link + Text[name_end_location+1:] 
    return Text


def listify (Text): # Goes through Text and turns Lists into HTML Lists
    while Text.find('[LIST: ') > -1:
        start_location = Text.find('[LIST: ')
        end_location = Text.find (']',start_location+1)
        List = Text[start_location+7:end_location]
        SubList = List
        while SubList.find(",, ") > -1:
            start = SubList.find (",, ")
            SubList = """</li>
            <li>""" + SubList[start+3:]
            List = List[:List.find(",, ")] + SubList 
        Text = Text[:start_location] + """
        
        <ol>
            <li>"""+ List +"""</li>
        </ol>
        
"""+Text[end_location+2:] 
    return Text



########################

######



def get_section (Text,Section_Number): # Get the entire section text (Title)
    count = 0
    Title = ""
    while count <= Section_Number:
        start_of_section = Text.find("TITLE: ")
        end_of_section = Text.find ("TITLE: ", start_of_section+1)
        if end_of_section >= 0:
            section = Text[start_of_section:end_of_section]
        else:
            end_of_section = len(Text)
            section = Text[start_of_section:]
        Text = Text[end_of_section:]
        count = count+1
    return section

def get_subsection (Section, SubSection_Number): # Get entire subsection text(Subject)
    subcount = 0
    while subcount <= SubSection_Number:
        start_of_subsection = Section.find("SUBJECT: ")
        end_of_subsection = Section.find("SUBJECT: ", start_of_subsection+1)
        if end_of_subsection >= 0:
            subsection = Section[start_of_subsection:end_of_subsection]
        else:
            end_of_subsection = len(Section)
            subsection = Section[start_of_subsection:]
        Section = Section[end_of_subsection:]
        subcount = subcount+1
    return subsection

    #########

def get_title (Section): # Gets the title of each section
    start_location = Section.find('TITLE: ')
    end_location = Section.find('SUBJECT: ')
    title = Section[start_location+7:end_location-1]
    return title

def get_subject (SubSection): # Gets the subject title of each subsection
    start_location = SubSection.find('SUBJECT: ')
    end_location = SubSection.find('DESCRIPTION: ')
    subject = SubSection[start_location+9:end_location-1]
    return subject

def get_description (SubSection): # Gets the description of each subsection
    start_location = SubSection.find('DESCRIPTION: ')
    end_location = SubSection.find('SUBJECT: ', start_location+1)
    if end_location >= 0:
        description = SubSection[start_location+13:end_location]
    else:
        end_location = len(SubSection)
        description = SubSection[start_location+13:end_location]
    SubSection = SubSection[end_location:]
    return description

def section_number (Text): # Gets the total number of sections
    total_sections = 0
    while Text.find('TITLE')>-1:
        total_sections = total_sections +1
        Text = Text[Text.find('TITLE')+1:]
    return total_sections

def get_subcount (Section): # Gets the total number of subsections
    subcount = 0
    while Section.find("SUBJECT: ") > -1:
        start_of_subject = Section.find("SUBJECT: ")
        Section = Section[start_of_subject+1:]
        subcount = subcount +1
    return subcount




def generate_TOC(Text): # Generates the Table of Contents
    Section_Number =0
    TOC = ""
    All_TOC= ""  
    while Section_Number < section_number(Text):
        Section = get_section (Text,Section_Number)   
        TOC = '''
    <li><a href="#" id="linkLesson-'''+str(Section_Number+1)+'"' + ">" + "Lesson " +str(Section_Number+1) + '''</a>
        '''
        # SubSection_Number =0
        # TOC_List = ""
        # while SubSection_Number < get_subcount(Section):
        #     SubSection = get_subsection (Section, SubSection_Number)
        #     TOC_List = TOC_List +'''
        #     <li><a href="#Lesson'''+ str(Section_Number+1) + '-' +str (SubSection_Number+1)+ '"'+ ">" + get_subject(SubSection) + "</a></li>"
        #     SubSection_Number = SubSection_Number+1
        Section_Number = Section_Number+1
        All_TOC = All_TOC + TOC + '''
    </li>'''
    return All_TOC


def generate_HTML (Text): # Generates the HTML code for the body
    Section_Number =0
    Title = ""
    ALL_HTML = ""
    while Section_Number < section_number(Text):
        Section = get_section (Text,Section_Number)
        Title = '''
    <div style="display:none"  id="Lesson-'''+str(Section_Number+1)+'"' + "><div class='TOC'><h2>" +  get_title(Section) + '''</h2><div class="InnerTOC">'''
        SubSection_Number=0
        HTML = ""
        while SubSection_Number < get_subcount(Section):
            SubSection = get_subsection(Section, SubSection_Number)
            HTML = HTML + '''
            <h3 id="Lesson'''+str(Section_Number+1)+ '-' +str (SubSection_Number+1)+ '"'+ ">"+ get_subject(SubSection)+'''</h3>
            <p>'''+get_description(SubSection)+"</p>"
            SubSection_Number = SubSection_Number+1
        Section_Number = Section_Number+1
        ALL_HTML = ALL_HTML + Title + HTML + "</div></div>"'''
    </div>'''
    return ALL_HTML

def process_html(processed_html, output_filename): # runs through all the HTML processing to be able to use the text files and outputs another procssed txt file for links and lists
    with open (output_filename, 'w') as f:
        f.write (processed_html)
        f.close ()
    return processed_html