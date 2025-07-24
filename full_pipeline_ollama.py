import logging
import argparse
from pathlib import Path
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    PictureDescriptionApiOptions,
)
from docling_core.types.doc.document import (
    PictureDescriptionData,
    PictureItem,
    TableItem,
    TextItem,
    DocItemLabel,
)


def main(args):
    """
    Main: args and pipeline
    """
    # --- 1. Setup ---
    logging.basicConfig(level=logging.INFO)
    _log = logging.getLogger(__name__)

    # Args
    doc_source = args.input
    output_dir = Path(args.output)
    vlm_prompt = args.vlm_prompt
    ollama_model = args.ollama_model

    output_dir.mkdir(parents=True, exist_ok=True)

    # Docling pipleine configuration
    _log.info("Docling pipeline configuration...")

    # Enabling image captioning with VLM
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_table_structure = True
    pipeline_options.do_ocr = False
    pipeline_options.do_picture_description = True
    pipeline_options.generate_picture_images = True
    pipeline_options.images_scale = 2.0

    # Local ollama is still considered as a remote service
    pipeline_options.enable_remote_services = True
    pipeline_options.picture_description_options = PictureDescriptionApiOptions(
        url="http://localhost:11434/v1/chat/completions",
        params=dict(
            model=ollama_model,  # Pulled ollama model
            temperature=0.2,
        ),
        prompt=vlm_prompt,
        timeout=120.0,
        provenance=f"Ollama ({ollama_model})",
    )

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options,
            )
        }
    )

    # Running the pipeline
    try:
        _log.info(f"Starting conversion for '{doc_source}'...")
        result = converter.convert(doc_source)
        doc = result.document
        _log.info("Conversion and captioning completed.")

        # Creating markdown file
        md_lines = [f"# {Path(doc_source).name}\n"]

        for item, level in doc.iterate_items():
            if isinstance(item, TextItem):
                if item.label == DocItemLabel.SECTION_HEADER:
                    md_lines.append(f"\n{'#' * (level + 1)} {item.text}\n")
                else:
                    md_lines.append(item.text)
            elif isinstance(item, TableItem):
                try:
                    table_df = item.export_to_dataframe()
                    md_lines.append(f"\n{table_df.to_markdown(index=False)}\n")
                except Exception as e:
                    _log.error(f"Unable to convert table : {e}")
            elif isinstance(item, PictureItem):
                pic_index = doc.pictures.index(item) + 1
                img_filename = f"image_{pic_index}.png"
                img_path = output_dir / img_filename
                try:
                    pil_img = item.get_image(doc)
                    if pil_img:
                        pil_img.save(img_path)
                        md_lines.append(f"\n![Image {pic_index}]({img_filename})")
                except Exception as e:
                    _log.error(f"Unable to save image {pic_index}: {e}")

                original_caption = item.caption_text(doc=doc)
                if original_caption:
                    md_lines.append(
                        f"\n*Original Caption : {original_caption.strip()}*\n"
                    )

                for annotation in item.annotations:
                    if isinstance(annotation, PictureDescriptionData):
                        md_lines.append(
                            f"**VLM Description :** {annotation.text.strip()}\n"
                        )

        # Write final markdown file
        output_md_path = output_dir / "full_document_report.md"
        with open(output_md_path, "w", encoding="utf-8") as f:
            f.write("\n\n".join(md_lines))

        _log.info(f"Markdown document successfully written to : {output_md_path}")

    except Exception as e:
        _log.error(f"An error occurred during the full pipeline : {e}", exc_info=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Traite un fichier PDF avec Docling pour en extraire le texte et sous-titrer les images.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--input", type=str, required=True, help="Chemin vers le fichier PDF d'entrée."
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Chemin vers le répertoire de sortie où les résultats seront sauvegardés.",
    )
    parser.add_argument(
        "--vlm-prompt",
        type=str,
        default="Describe this image with as much detail as possible.",
        help='Le prompt à utiliser pour le Vision Language Model (VLM).\n(défaut: "Describe this image with as much detail as possible.")',
    )

    # Specify Ollama model
    parser.add_argument(
        "--ollama-model",
        type=str,
        default="llava",
        help='Le nom du modèle multimodal à utiliser dans Ollama (ex: llava, llava:13b, etc.).\n(défaut: "llava")',
    )

    args = parser.parse_args()
    main(args)
