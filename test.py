import twspace_dl


# https://gist.github.com/dbr/256270
def test_filename():
    assert twspace_dl.FormatInfo.sterilize_fn("test.avi") == "test.avi"
    assert twspace_dl.FormatInfo.sterilize_fn("Test File.avi") == "Test File.avi"
    assert twspace_dl.FormatInfo.sterilize_fn("Test") == "Test"

    assert twspace_dl.FormatInfo.sterilize_fn("Test/File.avi") == "Test_File.avi"
    assert twspace_dl.FormatInfo.sterilize_fn("Test/File") == "Test_File"

    assert twspace_dl.FormatInfo.sterilize_fn("Test/File.avi") == "Test_File.avi"
    assert twspace_dl.FormatInfo.sterilize_fn('\\/:*?<Evil>|"') == "______Evil___"
    assert twspace_dl.FormatInfo.sterilize_fn("COM2.txt") == "_COM2.txt"
    assert twspace_dl.FormatInfo.sterilize_fn("COM2") == "_COM2"

    assert twspace_dl.FormatInfo.sterilize_fn(".") == "_."
    assert twspace_dl.FormatInfo.sterilize_fn("..") == "_.."
    assert twspace_dl.FormatInfo.sterilize_fn("...") == "_..."
