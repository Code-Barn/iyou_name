import os
import sys
import django
from io import BytesIO

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.generator.models import GedcomFile
from apps.generator.utils import image_4generator
from apps.parser.models import PersonData

def test_pdf_generation():
    """Test PDF generation using image_4generator.py."""
    try:
        # Get the first GEDCOM file from the database
        gedcom_file = GedcomFile.objects.first()
        if not gedcom_file:
            print("ERROR: No GEDCOM files found in the database.")
            return

        # Get the parsed_data (already a dictionary)
        family_data = gedcom_file.parsed_data
        if not family_data:
            print("ERROR: No family data found in the GEDCOM file.")
            return

        # Extract the 'individuals' dictionary
        individuals = family_data.get('individuals', {})
        if not individuals:
            print("ERROR: No individuals found in the family data.")
            return

        # Get the first individual
        first_individual_id = next(iter(individuals))
        first_individual_data = individuals[first_individual_id]
        print(f"Using individual: {first_individual_id}")
        print(f"Individual data: {first_individual_data}")

        # Convert to PersonData object
        primary_individual = PersonData(**first_individual_data)

        # Generate the family tree PDF
        print("Generating PDF...")
        image_buffer = image_4generator.generate_family_tree(
            primary_individual, family_data, template="4gen"
        )
        image_buffer.seek(0)

        # Save the PDF to a file
        output_path = os.path.join(os.path.dirname(__file__), 'family_tree.pdf')
        with open(output_path, 'wb') as f:
            f.write(image_buffer.getvalue())

        print(f"SUCCESS: PDF generated and saved to {output_path}")

    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_generation()
