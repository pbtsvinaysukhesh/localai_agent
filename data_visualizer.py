import matplotlib.pyplot as plt
import os
import json

class DataVisualizer:
    def __init__(self, output_dir="output/charts"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_chart(self, chart_type: str, chart_data_json: str, filename: str) -> str | None:
        """
        Generates a chart image from a JSON string of data.

        Args:
            chart_type (str): The type of chart to generate (e.g., 'bar', 'pie').
            chart_data_json (str): A JSON string containing chart details like title, labels, and data.
            filename (str): The base filename for the output image.

        Returns:
            The file path of the generated chart or None if failed.
        """
        try:
            chart_data = json.loads(chart_data_json)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON provided for chart data. {e}")
            return None

        plt.style.use('seaborn-v0_8-talk') # Use a professional style
        fig, ax = plt.subplots(figsize=(10, 6), dpi=150) # High-quality figure

        try:
            if chart_type.lower() == 'bar':
                labels = list(chart_data['data'].keys())
                values = list(chart_data['data'].values())
                ax.bar(labels, values)
                ax.set_ylabel(chart_data.get('y_label', 'Values'))
                ax.tick_params(axis='x', rotation=45)

            elif chart_type.lower() == 'pie':
                labels = list(chart_data['data'].keys())
                values = list(chart_data['data'].values())
                ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
                ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

            else:
                print(f"Error: Unsupported chart type '{chart_type}'")
                return None
            
            ax.set_title(chart_data.get('title', 'Untitled Chart'), pad=20)
            ax.set_xlabel(chart_data.get('x_label', ''))
            
            fig.tight_layout() # Adjust layout to prevent labels overlapping

            filepath = os.path.join(self.output_dir, f"{filename}.png")
            fig.savefig(filepath)
            plt.close(fig) # Close the figure to free up memory
            print(f"Chart saved to {filepath}")
            return filepath

        except Exception as e:
            print(f"An error occurred during chart generation: {e}")
            plt.close(fig)
            return None