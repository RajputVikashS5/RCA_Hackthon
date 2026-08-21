from langchain_text_splitters import RecursiveCharacterTextSplitter


class DocumentChunker:

    def __init__(self):

        self.text_splitter = RecursiveCharacterTextSplitter(

            chunk_size=800,

            chunk_overlap=150,

            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                ""
            ]
        )

    def chunk_text(self, text: str):

        return self.text_splitter.split_text(text)

    def chunk_documents(self, documents):

        all_chunks = []

        for document in documents:

            chunks = self.chunk_text(document["text"])

            for chunk in chunks:

                all_chunks.append({

                    "filename": document["filename"],
                    "page": document["page"],
                    "content": chunk

                })

        return all_chunks