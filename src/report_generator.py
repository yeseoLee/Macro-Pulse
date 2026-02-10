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

def generate_telegram_summary(data, mode='Global'):
    """
    Generates a text summary for Telegram based on the mode (KR or US).
    """
    
    def _format_line(item):
        price = item.get('price')
        change_pct = item.get('change_pct')
        
        if price is None:
            return f"{item['name']}: N/A"
            
        # Format Price
        if 'KRW' in item['name'] or 'Yen' in item['name'] or item['name'] in ['KOSPI', 'KOSDAQ', 'Nikkei 225', 'Hang Seng', 'Shanghai Composite', 'Bitcoin', 'Gold', 'Silver', 'S&P 500', 'Nasdaq', 'Euro Stoxx 50']:
             p_str = f"{price:,.2f}"
        elif 'Bond' in item['name'] or 'Treasury' in item['name'] or 'Year' in item['name']:
             p_str = f"{price:.3f}"
        else:
             p_str = f"{price:,.2f}"

        # Format Change
        if change_pct is not None and change_pct != 0:
            c_str = f"({change_pct:+,.2f}%)"
            return f"{item['name']}: {p_str} {c_str}"
        else:
            return f"{item['name']}: {p_str}"

    lines = []

    # Helper to find items by name in a category list
    def get_items(category, names):
        found = []
        source_list = data.get(category, [])
        for name in names:
            for item in source_list:
                if item['name'] == name:
                    found.append(item)
                    break
        return found

    if mode == 'KR':
        # [국내 증시]
        lines.append("[국내 증시]")
        for item in get_items('indices_domestic', ['KOSPI', 'KOSDAQ']):
             lines.append(_format_line(item))
        lines.append("")

        # [해외 증시] (Asia)
        lines.append("[해외 증시]")
        for item in get_items('indices_overseas', ['Nikkei 225', 'Hang Seng', 'Shanghai Composite']):
             lines.append(_format_line(item))
        lines.append("")

        # [변동성]
        lines.append("[변동성]")
        for item in get_items('volatility', ['VKOSPI', 'VIX']):
             lines.append(_format_line(item))
        lines.append("")

        # [채권]
        lines.append("[채권]")
        for item in get_items('commodities_rates', ['Japan 10Y Treasury', 'Korea 10Y Treasury']):
             lines.append(_format_line(item))
        lines.append("")

        # [환율]
        lines.append("[환율]")
        for item in get_items('exchange', ['USD/KRW', 'JPY/KRW']):
             lines.append(_format_line(item))

    elif mode == 'US':
        # [해외 증시] (US/EU)
        lines.append("[해외 증시]")
        for item in get_items('indices_overseas', ['S&P 500', 'Nasdaq', 'Euro Stoxx 50']):
             lines.append(_format_line(item))
        lines.append("")

        # [변동성]
        lines.append("[변동성]")
        for item in get_items('volatility', ['VKOSPI', 'VIX']):
             lines.append(_format_line(item))
        lines.append("")

        # [채권, 원자재]
        lines.append("[채권, 원자재]")
        for item in get_items('commodities_rates', ['US 10Y Treasury', 'Gold', 'Silver', 'Copper']):
             lines.append(_format_line(item))
        lines.append("")

        # [환율]
        lines.append("[환율]")
        for item in get_items('exchange', ['USD/KRW', 'JPY/KRW']):
             lines.append(_format_line(item))
        lines.append("")

        # [암호화폐]
        lines.append("[암호화폐]")
        for item in get_items('crypto', ['Bitcoin', 'Ethereum']):
             lines.append(_format_line(item))

    return "\n".join(lines)

if __name__ == "__main__":
    # Test
    pass
