from src.ingestion.chunking_process import create_chunks

"""
ana proje dizininde "pytest" yaz terminale, otomatik testleri calistirir
"""

def test_create_chunks_basic():
    slides = [
        {"slide_number": 1, "text": "Merhaba dünya"},
        {"slide_number": 2, "text": "İkinci slayt"},
    ]

    chunks = create_chunks(slides, source_name="TestPDF")

    assert len(chunks) == 2
    assert chunks[0]["id"] == "TestPDF_slide_1"
    assert chunks[0]["text"] == "Merhaba dünya"
    assert chunks[0]["metadata"]["source"] == "TestPDF"
    assert chunks[0]["metadata"]["slide_number"] == 1