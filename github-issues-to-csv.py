import csv, requests, re
from httplib2 import Response

# repo: expected as user/repository or company/repository
repo = ''
# token: have a look here https://github.com/settings/tokens 
token = ''
out_path = "."
# first (there is a link pagination) github url. 
# in this case I'll download all issues 
# more filters available here: https://docs.github.com/en/rest/reference/issues#list-issues-for-a-repository) 
gh_url = f'https://api.github.com/repos/{repo}/issues?state=all'

# download JSON issues and write them properly
def handle_gh_request_and_write_issues(url: str) -> Response:
    response = requests.get(url, headers={'Authorization' : f'token {token}'})    
    if response.status_code == 200:
        for issue in response.json():
            writer.writerow([issue['number'], issue['state'], issue['title'], issue['body'], issue['created_at'], issue['closed_at']])
    else:
        print (f'{response.status_code} - {response.reason}')      

    return response  

# note headers - link: <https://api.github.com/repositories/000000000/issues?page=2>; rel="next", <https://api.github.com/repositories/000000000/issues?page=29>; rel="last"
def get_gh_issue_urls(response_headers: list) -> dict:
    pages = dict()
    if 'link' in response_headers:
        for slice in response_headers['link'].split(','):
            groups = re.search(r'<(.*)>; rel="(.*)"', slice).groups()
            pages[groups[1]] = groups[0]
    return pages;


file_path = f'{out_path}/{repo.replace("/", "-")}-issues.csv' 
file = open(file_path, 'w', encoding='utf-8', newline='')

writer = csv.writer(file)
writer.writerow(['id', 'State', 'Title', 'Body', 'Created At', 'Updated At', 'Closed At'])

# response headers contains first, previous, next, last pages 
gh_urls = dict()

while gh_url != None:
    print(f"Downloadin' from { gh_url }")

    # handle current page
    response = handle_gh_request_and_write_issues(gh_url)

    # check if we are at the EoL
    if 'last' in gh_urls and gh_url == gh_urls['last']:
        gh_url = None
        break

    # get links for next url
    gh_urls = get_gh_issue_urls(response.headers)

    if 'next' not in gh_urls:
        break;
    
    gh_url = gh_urls['next']

file.close()

print ('...aaaand done!')