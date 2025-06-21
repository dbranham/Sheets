import generateScoreFromMP3
from pathlib import Path

if __name__ == '__main__':
    filename = "Reference Scales_On C.mp3"
    filePath = Path(str(Path(__file__).parent) + "/" + filename)

    score = generateScoreFromMP3(filePath)

    xml_path = filePath.with_suffix('.xml')
    score.export_xml(xml_path)