import matplotlib.pyplot as plt
import io
import base64
from jinja2 import Environment, FileSystemLoader
import os
import matplotlib

# Use Agg backend for non-interactive environments
matplotlib.use('Agg')

def generate_sparkline(history):
    """
    Generates a sparkline image as a base64 string.
    """
    plt.figure(figsize=(2, 0.5))
    plt.plot(history, color='#2ecc71' if history[-1] >= history[0] else '#e74c3c', linewidth=2)
    plt.axis('off')
    plt.tight_layout(pad=0)
    
    img = io.BytesIO()
    plt.savefig(img, format='png', transparent=True)
    img.seek(0)
    plt.close()
    
    return base64.b64encode(img.getvalue()).decode('utf-8')

def generate_html_report(data, template_dir='src/templates'):
    """
    Generates the HTML report using Jinja2.
    """
    # Add sparklines to data
    for category, items in data.items():
        for item in items:
            if len(item.get('history', [])) > 1:
                item['sparkline'] = generate_sparkline(item['history'])
            else:
                 item['sparkline'] = "" # No sparkline
                 
            # Format numbers
            if item.get('price') is not None:
                if 'KRW' in item['name'] or 'Yen' in item['name']:
                    item['price_str'] = f"{item['price']:,.2f}"
                elif 'Bond' in item['name'] or 'Treasury' in item['name'] or 'Year' in item['name']:
                     item['price_str'] = f"{item['price']:.3f}"
                else:
                    item['price_str'] = f"{item['price']:,.2f}"
            else:
                item['price_str'] = ""

            if item.get('change') is not None:
                item['change_str'] = f"{item['change']:+,.2f}"
                item['change_pct_str'] = f"{item['change_pct']:+,.2f}%"
                item['color_class'] = 'positive' if item['change'] > 0 else 'negative' if item['change'] < 0 else 'neutral'
            else:
                item['change_str'] = ""
                item['change_pct_str'] = ""
                item['color_class'] = 'neutral'

    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('report.html')
    
    return template.render(data=data)

if __name__ == "__main__":
    # Test
    pass
