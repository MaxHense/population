from scripts.eurostat import cells

HEADER = "GRD_ID,T,M,F,CNTR_ID"


def test_cell_id_becomes_centre_of_the_cell():
    rows = [HEADER, "CRS3035RES1000mN2684000E4285000,25,14,12,AT-CH-LI"]
    assert list(cells(rows)) == [(4285500, 2684500, 25)]


def test_only_inhabited_cells_with_a_location_are_kept():
    rows = [
        HEADER,
        "CRS3035RES1000mN2683000E4285000,0,0,0,AT",      # nobody lives here
        "CRS3035RES1000mN2683000E4286000,-8888,0,0,AT",  # confidential
        "CRS3035RES1000mN2683000E4287000,-9999,0,0,AT",  # missing
        "FR_unallocated,1234,0,0,FR",                    # no geometry
        "CRS3035RES1000mN2683000E4288000,3,0,0,AT",
    ]
    assert list(cells(rows)) == [(4288500, 2683500, 3)]
