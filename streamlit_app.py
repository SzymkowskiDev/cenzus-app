import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib import colors
import os

# Utility function to create a ParagraphStyle
def create_paragraph_style(font_name, font_size, alignment='CENTER', leading=14):
    return ParagraphStyle(
        name=f"{font_name}_{font_size}",
        fontName=font_name,
        fontSize=font_size,
        alignment={'CENTER': 1, 'LEFT': 0, 'RIGHT': 2}.get(alignment, 1),
        leading=leading
    )

# Function to split and format the character name
def format_character_name(name):
    name_parts = name.split(' ', 1)  # Split into first word and the rest
    if len(name_parts) == 1:
        return f'<font size=14>{name_parts[0]}</font>'
    else:
        return f'<font size=14>{name_parts[0]}</font><br/><font size=10>{name_parts[1]}</font>'

# Function to generate census PDF
def generate_census(df, font_path, output_pdf):
    # Check if the font file exists
    if os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont('MedievalFont', font_path))
            font_name = 'MedievalFont'
        except Exception as e:
            st.error(f"Failed to load font: {e}")
            font_name = 'Helvetica'  # Fallback to default font
    else:
        st.error("Font file not found, using default font.")
        font_name = 'Helvetica'  # Fallback to default font

    # Filter records where the character should be included in the public census
    df = df[df.iloc[:, 4].str.contains("Tak", na=False)]

    # Group the data by faction
    factions = df.groupby('Frakcja')

    # Prepare the PDF document
    pdf = SimpleDocTemplate(output_pdf, pagesize=A4, rightMargin=2 * cm, leftMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm)
    elements = []

    # Create reusable paragraph styles
    title_style = create_paragraph_style(font_name, 22, alignment='CENTER')
    faction_style = create_paragraph_style(font_name, 16, alignment='CENTER')
    header_style = create_paragraph_style(font_name, 14, alignment='CENTER')
    character_name_style = create_paragraph_style(font_name, 10, alignment='CENTER')

    # Add title with extra space
    elements.append(Paragraph("Cenzus", title_style))
    elements.append(Spacer(1, 48))  # Add more space between the title and the rest

    # Iterate over each faction and create a table for its characters
    for faction, group in factions:
        # Add the faction name
        elements.append(Spacer(1, 12))  # Add space before the faction name
        elements.append(Paragraph(faction, faction_style))  # Display faction name
        elements.append(Spacer(1, 12))  # Add space between faction name and the table

        # Prepare table data with header
        table_data = [[Paragraph("Postać", header_style), Paragraph("Opis", header_style), Paragraph("Notatki", header_style)]]

        for _, row in group.iterrows():
            character_name = format_character_name(row['Jak nazywa się Twoja postać?'])
            description = row['Opis postaci (max 600 znaków)']
            table_data.append([Paragraph(character_name, character_name_style), description, ''])

        # Create the table with internal borders only and invisible external borders
        table = Table(table_data, colWidths=[5 * cm, 7.5 * cm, 7.5 * cm])  # Adjusted column widths

        # Define table style with invisible outer borders and visible internal gridlines
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Horizontal center alignment for all cells
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertical center alignment for all cells
            ('FONTNAME', (0, 0), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black),  # Internal gridlines
            ('BOX', (0, 0), (-1, -1), 0.25, colors.white),  # White outer borders (invisible)
            ('TEXTCOLOR', (0, 0), (-1, -1), 'black'),
        ]))

        # Add the table to the document
        elements.append(table)

    # Build the PDF
    pdf.build(elements)

# Streamlit app
st.title("Census PDF Generator")

# Upload CSV file
csv_file = st.file_uploader("Upload your CSV file", type="csv")

# Font path (you can adjust this)
font_path = "cenzus_tool/Berylium.ttf"  # Update with the correct path

# Button to generate PDF if CSV is uploaded
if csv_file is not None:
    df = pd.read_csv(csv_file)

    if st.button("Generate PDF"):
        # Generate the PDF
        output_pdf = "generated_census.pdf"
        generate_census(df, font_path, output_pdf)

        # Provide a download link for the PDF
        with open(output_pdf, "rb") as pdf_file:
            st.download_button(
                label="Download PDF",
                data=pdf_file,
                file_name=output_pdf,
                mime="application/pdf"
            )
