from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PictureDescriptionVlmOptions
from docling_core.types.doc.document import PictureDescriptionData

import logging 




# -----------------------------------------------------------------
# Program used to extract images from a given data source and caption
# them using a VLM.
# You can chose the VLM from Hugginface, but not every model is compatible
# especially for the VLMs that need to run external code (ex Florence2)
# -----------------------------------------------------------------

# Usage : put the document in DOC_SOURCE (web or local path)
# Put a save directory in SAVE_DIR
# The VLM prompt can be changed also in the pipeline options
# Run the program


DOC_SOURCE = ""
SAVE_DIR = "output"

logger = logging.getLogger(__name__)

pipeline_options = PdfPipelineOptions()
pipeline_options.do_picture_description = True
pipeline_options.picture_description_options = PictureDescriptionVlmOptions(
    repo_id="ibm-granite/granite-vision-3.3-2b",
    prompt="What is shown in this image?",
)
pipeline_options.images_scale = 2.0
pipeline_options.generate_picture_images = True

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=pipeline_options,
        )
    }
)

# Uncomment to run:
doc = converter.convert(DOC_SOURCE).document

md_lines = ["# Picture Description\n"]

for i, pic in enumerate(doc.pictures):
  img_path = f"{SAVE_DIR}/images/pic_{i}.png"
  pil_img = pic.get_image(doc)
  if pil_img is not None:
    pil_img.save(img_path)
  else:
    logger.warning(f"No image found for {pic}")

  md_lines.append(f"[Image {i}]({img_path})")
  md_lines.append(f"\n*Caption: {pic.caption_text(doc=doc)}*\n")
  for annotation in pic.annotations:
    if isinstance(annotation, PictureDescriptionData):
      md_lines.append(f"\n**Annotation ({annotation.provenance}):** {annotation.text}\n")

with open(f"{SAVE_DIR}/picture_description.md", "w", encoding="utf-8") as f:
  f.write("\n".join(md_lines))
