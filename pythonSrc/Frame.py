# Class definition for a Training Example
class Frame:
    """ Here I would write some class documentation, though I have not time at the moment. Let the
    future me swear his Miguel of the past for this laziness """

    def __init__(self, snr=0, label='SIL', sil_frame=True):
        self.snr = snr
        self.label = label
        self.sil_frame = sil_frame


class Utterance:
    def __init__(self, frames, audio, unit_name, events):
        self.frames = frames
        self.audio = audio
        self.unit_name = unit_name
        self.events = events