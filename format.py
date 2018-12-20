class IrcTextFormat:
    def __init__(self, string: str):
        self.__string = string

    @property
    def bold(self):
        return '\x02%s\x02' % self.__string

    @property
    def white(self):
        return '\x0300%s\x03' % self.__string

    @property
    def black(self):
        return '\x0301%s\x03' % self.__string

    @property
    def blue(self):
        return '\x0302%s\x03' % self.__string

    @property
    def green(self):
        return '\x0303%s\x03' % self.__string

    @property
    def red(self):
        return '\x0304%s\x03' % self.__string

    @property
    def brown(self):
        return '\x0305%s\x03' % self.__string

    @property
    def purple(self):
        return '\x0306%s\x03' % self.__string

    @property
    def orange(self):
        return '\x0307%s\x03' % self.__string

    @property
    def yellow(self):
        return '\x0308%s\x03' % self.__string

    @property
    def light_green(self):
        return '\x0309%s\x03' % self.__string

    @property
    def teal(self):
        return '\x0310%s\x03' % self.__string

    @property
    def light_cyan(self):
        return '\x0311%s\x03' % self.__string

    @property
    def light_blue(self):
        return '\x0312%s\x03' % self.__string

    @property
    def pink(self):
        return '\x0313%s\x03' % self.__string

    @property
    def grey(self):
        return '\x0314%s\x03' % self.__string

    @property
    def light_grey(self):
        return '\x0315%s\x03' % self.__string
