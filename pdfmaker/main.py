import flet as ft
from flet import FilePicker, FilePickerResultEvent, Page, Text, ElevatedButton, Column, Row, TextField, AlertDialog, Container
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from PIL import Image as PILImage
import webbrowser  # For opening WhatsApp web

def main(page: Page):

    def save_images_to_pdf(images, output_pdf_path):
        output_folder = os.path.join(os.path.expanduser("~"), "PDF_Files")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        output_pdf_path = os.path.join(output_folder, output_pdf_path)

        c = canvas.Canvas(output_pdf_path, pagesize=letter)
        width, height = letter

        for image_path in images:
            img = PILImage.open(image_path)
            img_width, img_height = img.size
            aspect = img_height / float(img_width)

            if aspect > 1:
                img_width = width
                img_height = width * aspect
            else:
                img_height = height
                img_width = height / aspect

            img = img.resize((int(img_width), int(img_height)), PILImage.LANCZOS)
            img_path = image_path.replace(os.path.splitext(image_path)[1], ".jpg")
            img.save(img_path, "JPEG")
            c.drawImage(img_path, 0, 0, width=width, height=height)
            c.showPage()
            os.remove(img_path)

        c.save()
        return output_pdf_path

    def clear_all():
        selected_images.clear()
        images_column.controls.clear()
        output_path_field.value = "output.pdf"

    selected_images = []

    def pick_files_result(e: FilePickerResultEvent):
        if e.files:
            for f in e.files:
                selected_images.append(f.path)
                images_column.controls.append(ft.Image(src=f.path, width=100, height=100))
            page.update()

    def create_pdf(e):
        if not selected_images:
            error_dialog = AlertDialog(
                title=Text("Error"),
                content=Text("Please select some images first."),
                actions=[ElevatedButton(text="OK", on_click=lambda _: close_dialog())]
            )
            page.dialog = error_dialog
            error_dialog.open = True
            page.update()
            return

        output_pdf_path = output_path_field.value
        if not output_pdf_path.endswith('.pdf'):
            output_pdf_path += '.pdf'
        
        output_pdf_path = save_images_to_pdf(selected_images, output_pdf_path)
        
        success_dialog = AlertDialog(
            title=Text("Success"),
            content=Text(f"PDF created successfully: {output_pdf_path}"),
            actions=[
                ElevatedButton(text="OK", on_click=lambda _: close_dialog()),
                ElevatedButton(text="Share", on_click=lambda _: share_pdf(output_pdf_path))
            ]
        )
        page.dialog = success_dialog
        success_dialog.open = True
        page.update()
        
        # Display the converted PDF file
        pdf_column.controls.append(Text(output_pdf_path))
        page.update()

        # Clear selected images and reset output PDF path
        clear_all()

    def reset(e):
        clear_all()
        page.update()

    def close_dialog():
        page.dialog.open = False
        page.dialog = None  # Clear the dialog from the page
        page.update()

    def share_pdf(output_pdf_path):
        # Sharing via WhatsApp web (for demonstration purposes)
        message = f"Here's the PDF file: {output_pdf_path}"
        webbrowser.open(f"https://wa.me/?text={message}")

    images_column = Column()
    pdf_column = Column()
    output_path_field = TextField(label="Output PDF Path", value="output.pdf")

    file_picker = FilePicker(on_result=pick_files_result)

    page.overlay.append(file_picker)
    
    page.add(
        Container(
            content=Column([
                Row([
                    ElevatedButton("Select Images", on_click=lambda _: file_picker.pick_files(allow_multiple=True, file_type=ft.FilePickerFileType.IMAGE))
                ]),
                Row([
                    output_path_field
                ]),
                Row([
                    ElevatedButton("Create PDF", on_click=create_pdf),
                    ElevatedButton("Reset", on_click=reset),
                ]),
                Row([
                    Text("Converted PDF files:"),
                    pdf_column
                ]),
                images_column,
            ]),
            alignment=ft.alignment.center,
            padding=20
        )
    )

ft.app(target=main)
