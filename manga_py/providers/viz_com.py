from manga_py.provider import Provider
from .helpers.std import Std
from manga_py.fs import get_util_home_path, path_join, is_file, unlink
from sys import stderr
from manga_py import meta


class VizCom(Provider, Std):
    cookie_file = None
    __cookies = {}

    def get_chapter_index(self) -> str:
        # return str(self.chapter_id)
        # todo: need tests
        idx = str(self.chapter_id)
        try:
            re = self.re.compile(r'-chapter-(\d+)/')
            idx = re.search(self.chapter).group(1)
        except AttributeError:
            print('manga-py can not get the number of the chapter!\nurl: {}'.format(self.chapter), file=stderr)
            print(' Please, report this error\n {}{}\n\n'.format(
                meta.__downloader_uri__, '/issues/new?template=bug_report.md'
            ), file=stderr)
        return idx

    def get_main_content(self):
        return self._get_content('{}/shonenjump/chapters/{}')

    def get_manga_name(self) -> str:
        return self._get_name('/chapters/([^/]+)')

    def get_chapters(self):
        return self._elements('a.flex[href*="/chapter/"],a.pad-r-rg.o_chapter-container[href*="/chapter/"]')

    def get_files(self):
        print(self.get_chapter_index())

    def get_cover(self):
        self._cover_from_content('.o_hero-media')

    def prepare_cookies(self):
        self.cookie_file = path_join(get_util_home_path(), 'cookies_viz_com.dat')
        cookies = self.load_cookies()
        content = self.http().requests(self.get_url(), cookies=cookies)
        cookies.update(content.cookies.get_dict())
        self.__cookies = cookies

        if not self.has_auth():
            self.auth()
            if not self.has_auth():
                print('Warning! Login/password incorrect?\nTry to get free chapters...', file=stderr)
                print('Warning! This site worked from USA and Japan! Check your location', file=stderr)
                unlink(self.cookie_file)
                return

        self.save_cookies(self.__cookies)
        self.http().cookies = self.__cookies

    def auth(self):
        token = self.get_token()

        # name = self.quest([], 'Request login on viz.com')
        # password = self.quest_password('Request password on viz.com\n')

        name = 'sttvpc'
        password = 'iO2164nlYn3TVuE'

        req = self.http().requests('https://www.viz.com/account/try_login', method='post', cookies=self.__cookies, data={
            'login': name,
            'pass': password,
            'rem_user': 1,
            'authenticity_token': token,
        })
        with open('req.txt', 'wb') as w:
            w.write(req.content)

        if req.status_code >= 400:
            print('Login/password error')
            exit(1)

        self.__cookies = req.cookies.get_dict()

        try:
            remember = self.json.loads(req.text)
            self.__cookies['remember_token'] = remember['trust_user_id_token_web']
        except ValueError:
            print('Remember error!', file=stderr)
            print('Please, report this error {}{}'.format(
                meta.__downloader_uri__, '/issues/new?template=bug_report.md'
            ), file=stderr)

    def save_cookies(self, cookies: dict):
        with open(self.cookie_file, 'w') as w:
            w.write(self.json.dumps(cookies))

    def load_cookies(self):
        if is_file(self.cookie_file):
            try:
                with open(self.cookie_file, 'r') as r:
                    return self.json.loads(r.read())
            except ValueError:
                unlink(self.cookie_file)
        return {}

    def get_token(self):
        auth_token_url = 'https://www.viz.com/account/refresh_login_links'
        auth_token = self.http().get(auth_token_url, cookies=self.__cookies)
        token = self.re.search(r'AUTH_TOKEN\s*=\s*"(.+?)"', auth_token)
        return token.group(1)

    def has_auth(self):
        content = self.http_get('https://www.viz.com/account/refresh_login_links', cookies=self.__cookies)
        parser = self.document_fromstring(content)
        profile = parser.cssselect('.o_profile-link')
        success = len(profile) > 0
        if success:
            print('Login as {}'.format(profile[0].text))
        return success

    @staticmethod
    def has_chapters(parser):
        return len(parser.cssselect('.o_chapter-container')) > 0


main = VizCom
