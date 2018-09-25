import logging

log = logging.getLogger(__name__.split(".")[-1])


class Export:
    def __init__(self):
        pass

    def export(self, filename, moves):
        log.info("Exporting to %s", filename)
        f = open(filename, "wt")
        f.write(";NinjaKittens3 export!\n")
        for move in moves:
            if move.xy is None:
                f.write("G1 F%d Z%f\n" % (move.speed, move.z))
            else:
                f.write("G1 F%d X%f Y%f Z%f\n" % (move.speed, move.xy.real, move.xy.imag, move.z))
        f.close()
