from dataclasses import dataclass

@dataclass(frozen=True)
class Message:
    cmd: str
    arg: str = ''

    def reply_cmd(self) -> str:
        return self.cmd.upper()

    def encode(self) -> bytes:
        return ("%s:%s\r\n" % (self.cmd, self.arg)).encode('utf-8')

    @staticmethod
    def decode(line: bytes) -> 'Message':
        comps = line.decode('utf-8').strip().split(':', 1)
        return Message(comps[0], comps[1] if len(comps) > 1 else '')
