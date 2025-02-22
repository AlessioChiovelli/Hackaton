from . import  st

def render_css(file_path):
    with open(file_path, 'r') as file:
        css_content = file.read()
        st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)

# Example usage
if __name__ == "__main__":
    render_css('path_to_your_css_file.css')