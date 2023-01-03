import i18n

i18n.load_path.append('src/i18n/')
i18n.set('file_format', 'yaml')
i18n.set('default_locale', 'en')


class I18n:
    def __init__(self, locale: str, filename: str = 'text_messages') -> None:
        self.locale = locale
        self.filename = filename
        i18n.set('filename_format', '%{self.filename}.%{format}')
        i18n.set('locale', self.locale)

    def t(self, key: str, placeholder: dict = None) -> str:
        if placeholder:
            # verify that placeholder keys has values
            for k, v in placeholder.items():
                if v is None or v == '':
                    raise ValueError(f'Placeholder key {k} has no value')
            try:
                return i18n.t(key, **placeholder)
            except Exception:
                i18n.set('locale', 'en')
                return i18n.t(key, **placeholder)
        try:
            return i18n.t(key)
        except Exception:
            i18n.set('locale', 'en')
            return i18n.t(key)

    def update(self, locale: [str, None] = None, filename: [str, None] = None):
        self.locale = locale if locale else self.locale
        self.filename = filename if filename else self.filename
        self.__init__(self.locale, self.filename)
        return self
