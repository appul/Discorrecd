from discorrecd.discorrecd import Discorrecd
from discorrecd.modules.testmodule import TestModule


def main():
    discorrecd = Discorrecd()
    discorrecd.initialize()
    discorrecd.core.add(TestModule)
    discorrecd.start()


if __name__ == '__main__':
    main()
