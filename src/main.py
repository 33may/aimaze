import os
from urllib.parse import urljoin

from validators import url as validate_url

from gen.gen import extract_schemas, generate_code
from scrape import bfs_site


# api_name = "Github Actions"
# base_url = "https://api.github.com/"
# output_file_loc = "test/gh.py"
# documentation_domains = [
#     ("https://docs.github.com/en/rest/actions/artifacts?apiVersion=2022-11-28", "https://docs.github.com/en/rest/actions"),
#     ("https://docs.github.com/en/rest/authentication/endpoints-available-for-github-app-installation-access-tokens?apiVersion=2022-11-28", "https://docs.github.com/en/rest/authentication"),
# ]


# api_name = "Woo commerce"
# base_url = "https://woocommerce.github.io/woocommerce-rest-api-docs"
# output_file_loc = "test/woo_test.py"
# documentation_domains = [ ("https://woocommerce.github.io/woocommerce-rest-api-docs" , "")]


api_name = "WebWinkel"
base_url = "https://docs.webwinkelkeur.nl"
output_file_loc = "test/webwinkel.py"
documentation_domains = [ ("https://docs.webwinkelkeur.nl" , "")]

# api_name = "anewspring"
# base_url = "https://docs.webwinkelkeur.nl"
# output_file_loc = "test/webwinkel.py"
# documentation_domains = [ ("https://docs.webwinkelkeur.nl" , "")]


# api_name = "Pipe"
# base_url = "Https://developers.pipedrive.com"
# output_file_loc = "test/pipe.py"
# documentation_domains = [ ("Https://developers.pipedrive.com" , "/docs/api/v1")]



def main():
    os.system("clear")

    print("Tool is running, this could take a couple of minutes.")
    pages = {}

    for starting_url, domain_url in documentation_domains:
        pages.update(bfs_site(starting_url, domain_url))

    schemas = extract_schemas(pages)
    generate_code(schemas, base_url, api_name, output_file_loc)
    print(f"Code generated and saved at {output_file_loc}")


def get_valid_url(prompt: str) -> str:
    while True:
        url = input(prompt)

        if validate_url(url):
            return url

        print("Invalid URL")
                

def main_menu():
    global api_name, base_url, output_file_loc

    while True:
        os.system("clear")
        action = input(f"""
        This tool will scrape the documentation of a selected API and generate Python code to call it. Please set the following information:

         (1) API Name: {api_name or "not set"}
         (2) API Base URL: {base_url or "not set"}
         (3) Output file location: {output_file_loc or "not set"}
         (4) Documentation website domains: 
             {"\n\n             ".join([f"- Starting URL: {start}\n               Domain: {domain}"
                                for start, domain in documentation_domains]) or "not set"}
               
         {"(C)onfirm" if all([api_name, base_url, output_file_loc, documentation_domains]) else "All fields above are required before processing."}
         (E)xit

        """)
        
        match action.lower()[0]:
            case "1":
                api_name = input("Please enter the API name: ")
                
            case "2":
                base_url = get_valid_url("Please enter the API base URL: ")
                
            case "3":
                while True:
                    output_file_loc = input("Please enter the output Python file location: ").strip()
                    
                    if not output_file_loc.endswith(".py"):
                        if not output_file_loc.endswith("/"):
                            output_file_loc += "/"
                        output_file_loc += "api_wrapper.py"
                    
                    try:
                        open(output_file_loc, "w")
                        break
                    except:
                        print("Invalid file location.")
            case "4":
                domain_menu()
                
            case "c" if all([api_name, base_url, output_file_loc, documentation_domains]):
                if input("Are you sure these fields are correct? [y]es, [n]o\n").lower()[0] == "y":
                    os.system(f"touch {output_file_loc}")
                    main()
                    exit()

            case "e":
                if input("Are you sure you want to exit? [y]es, [n]o\n").lower()[0] == "y":
                    exit()

            case ":" if action.lower()[1] == "q":
                exit()
            

def domain_menu():
    global documentation_domains

    while True:
        os.system("clear")
        action = input(f"""
        The scraper performs a breadth-first search on all links it finds, within the specified domain.

        ADD MORE EXPLANATION AND EXAMPLES.

        Current domains: 
         {"\n\n         ".join([f"({i+1}) Starting URL: {start}\n             Domain: {domain}"
                        for i, (start, domain) in enumerate(documentation_domains)])}

         (A)dd new domain{"\n         (R)emove domain" if len(documentation_domains) else ""}{"\n         (E)hange domain" if len(documentation_domains) else ""}        

         (B)ack to main menu

        """)

        match action.lower()[0]:
            case "a":
                while True:
                    starting_url = get_valid_url("Please enter starting URL: ")
                    domain_url = get_valid_url("Please enter domain URL: ")
                    
                    if starting_url.startswith(urljoin(starting_url, domain_url)):
                        break

                    print("Starting URL outside of domain, entry is invalid. Please try again.")

                documentation_domains.append((starting_url, domain_url))

            case "r" if len(documentation_domains):
                while True:
                    index = input("Please enter the index of the domain to remove: ")
                    if index.isnumeric():
                        index = int(index) - 1
                        if index < len(documentation_domains):
                            break
                    print(f"Invalid input '{index}', expected 1-{len(documentation_domains)}.")

                documentation_domains.pop(index)
                
            case "e" if len(documentation_domains):
                while True:
                    index = input("Please enter the index of the domain edit: ")
                    if index.isnumeric():
                        index = int(index) - 1
                        if index < len(documentation_domains):
                            break
                    print(f"Invalid input '{index}', expected 1-{len(documentation_domains)}.")
                
                looping = True
                while looping:
                    starting_url, domain_url = documentation_domains[index]

                    if input("Do you wish to edit the starting URL? [y]es, [n]o\n").lower()[0] == "y":
                        starting_url = get_valid_url("Please enter new starting URL: ")

                    if input("Do you wish to edit the domain URL? [y]es, [n]o\n").lower()[0] == "y":
                        domain_url = get_valid_url("Please enter new domain URL: ")
                    
                    action = input("Are you sure these settings are correct? [y]es, [r]etry, [c]ancel\n").lower()[0]
                    
                    match action:
                        case "y" if not starting_url.startswith(urljoin(starting_url, domain_url)): 
                            print("Starting URL outside of domain, entry is invalid. Please try again.")

                        case "y":
                            documentation_domains.pop(index)
                            documentation_domains.insert(index, (starting_url, domain_url))
                            looping = False
                        
                        case "c":
                            looping = False
                            

            case "b":
                return
                
            
main_menu()
