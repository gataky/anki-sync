import attr


@attr.s(auto_attribs=True, frozen=True)
class AudioMeta:

    phrase: str
    filename: str
