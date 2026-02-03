class Section:
    def __init__(self, text: str):
        self.text = text

def sectionize(paragraphs: list[str]) -> list[Section]:
    return [Section(p) for p in paragraphs]
