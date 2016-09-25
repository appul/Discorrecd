from discorrecd.discorrecd import Discorrecd
from discorrecd.modules.customemoticonsmodule import CustomEmoticonsModule


def main():
    discorrecd = Discorrecd()
    discorrecd.initialize()
    discorrecd.core.add(CustomEmoticonsModule)
    discorrecd.start()


if __name__ == '__main__':
    main()
