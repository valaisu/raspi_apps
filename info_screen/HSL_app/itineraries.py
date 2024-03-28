import requests
import json
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageTk
from tkinter import Tk, Label, Button
import sys

from secret_info import TOKEN1, HOME, AALTO, GYM_CENTER, PRISMA

BASE_URL = "https://api.digitransit.fi/routing/v1/routers/hsl/index/graphql"
LIGHT_BLUE = '#45c3f5'
DARK_BLUE = '#1e78d9'
VIOLET = '#a320bd'


def find_routes(start_coord: tuple[float, float], end_coord: tuple[float, float], 
                day: str = datetime.today().strftime("%Y-%m-%d"), time: str = datetime.now().strftime("%H:%M:%S"), token: str = TOKEN1,
                walk_speed: float = 2.0, min_transfer_time: int = 0, amount: int = 5):
    """
    Requests itineraries from start_coord to end_coord 
    :param start_coord: 
    :param end_coord: 
    :param day: 
    :param time: your earliest departure time
    :param token: access token
    :param walk_speed: 
    :param min_transfer_time: 
    :param amount: of itineraries shown, server might 1 less 
    :return: 
    """
    
    graphql_query = f"""
    {{
        plan(
            from: {{lat: {start_coord[0]}, lon: {start_coord[1]}}},
            to: {{lat: {end_coord[0]}, lon: {end_coord[1]}}},
            date: "{day}",
            time: "{time}",
            numItineraries: {amount},
            transportModes: [{{mode: BUS}}, {{mode: RAIL}}, {{mode:TRAM}}, {{mode:WALK}}]
            walkReluctance: 1.0,
            walkBoardCost: 120,
            minTransferTime: {min_transfer_time},
            walkSpeed: {walk_speed},
        ) {{
            itineraries {{
                duration
                legs {{
                    mode
                    startTime
                    endTime
                    from {{
                        name
                    }}
                    to {{
                        name
                    }}
                    trip {{
                        routeShortName
                    }}
                }}
            }}
        }}
    }}
    """
    response = requests.post(
        url=BASE_URL,
        headers={"Content-Type": "application/json", "digitransit-subscription-key": token},
        data=json.dumps({"query": graphql_query})
    )
    response.raise_for_status()
    return response.json()


def routes_graphical_representation(data, bar_height: int = 30, bar_medium: int = 15, window_size: int = 300, padding: int = 25):

    # first parse date into formats:
    # instructions = list[list[start_time, end_time, route_name, tansport_mode]]
    # where an element outer list is a full route and an element inner list is a bus ride / walk / etc.
    # durations = list[start_time: str, duration: str]

    itineraries = data['data']['plan']['itineraries']
    instructions = []
    duration_data = []
    now = int(datetime.now().timestamp())
    last_arrival = 0
    for itinerary in itineraries:
        duration = (int((itinerary['legs'][-1]['endTime'] - itinerary['legs'][0]['startTime'])/60000))
        start = datetime.fromtimestamp(itinerary['legs'][0]['startTime'] / 1000).strftime('%H:%M')        
        duration_data.append(f"{start}, {duration} min")
        route_info = []
        for leg in itinerary['legs']:
            mode = leg['mode']
            start_time = int(leg['startTime'] / 1000)
            end_time = int(leg['endTime'] / 1000)
            if (end_time > last_arrival): last_arrival = end_time
            route_name = leg['trip']['routeShortName'] if leg['trip'] else ''
            vehicle = [start_time, end_time, route_name, mode]
            route_info.append(vehicle)
        
        instructions.append(route_info)
    
    # transfer to graphical instructions
    # boxes = list[x_up_corner: int, y_up_corner: int, x_low_corner: int, y_low_corner: int, trnasport_line: str, transport_mode: str]
    # the list is named boxes
    time_window = last_arrival - now  # in seconds
    element_counter = 0
    boxes = []
    color_dict = {'WALK': 'grey', 'BUS': 'blue', 'TRAM': 'green', 'RAIL': VIOLET}
    for instr in instructions:
        for vehicle in instr:
            start_pos_x = padding + int(window_size*(vehicle[0]-now)/time_window)
            end_pos_x = padding + int(window_size*(vehicle[1]-now)/time_window)
            start_pos_y = padding + element_counter*(bar_height+bar_medium)
            end_pos_y = padding + element_counter*(bar_height+bar_medium) + bar_height
            if start_pos_x < end_pos_x and start_pos_y < end_pos_y:
                boxes.append([start_pos_x, start_pos_y, end_pos_x, end_pos_y, vehicle[2], color_dict[vehicle[3]]])
        element_counter += 1

    # draw 
    img = Image.new('RGB', (450, 300), color=DARK_BLUE)
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", 12)
    
    # borders
    d.rounded_rectangle([padding-10, padding-10, padding+10+window_size, len(itineraries)*(bar_height+bar_medium)+bar_height+10], outline=LIGHT_BLUE, fill=LIGHT_BLUE, width=2, radius=3)

    # transport
    for b in boxes:
        try:
            d.rounded_rectangle([b[0], b[1], b[2], b[3]], outline=b[5], fill=b[5], width=3, radius=3)
            x_center = int((b[0]+b[2])/2)
            y_center = int((b[1]+b[3])/2)
            d.text((x_center-len(b[4])*3, y_center-6), b[4], fill='white', font=font)
        except ValueError:
            print("B incoming")
            print(b)
            print("-------")

    # durations
    for i, text in enumerate(duration_data):
        x_pos = window_size+padding+30
        y_pos = padding + 6 + i*(bar_height+bar_medium)
        d.text((x_pos, y_pos), text, fill='black', font=font)
        # lines between itineraries
        y = padding+bar_medium*2.5+(bar_height+bar_medium)*i
        d.line([(padding, y), (padding+window_size, y)], fill=DARK_BLUE, width=1)

    return img


def show_image_pil_upper_left(image_pil):

    root = Tk()
    root.overrideredirect(True)  # Remove window decorations    
    root.geometry("+0+0")  # upper left corner

    photo = ImageTk.PhotoImage(image_pil)
    label = Label(root, image=photo)
    label.pack(side="top", fill="both", expand="yes")    
    label.config(borderwidth=0, highlightthickness=0)
    
    button_quit = Button(root, text="Close", command=root.destroy)
    button_quit.pack(side="bottom", fill="none", expand="yes")
    
    root.mainloop()


def get_routes(start_coord: tuple[float, float], end_coord: tuple[float, float], 
                day: str = datetime.today().strftime("%Y-%m-%d"), time: str = datetime.now().strftime("%H:%M:%S"), token: str = TOKEN1,
                walk_speed: float = 2.0, min_transfer_time: int = 0, amount: int = 5):
    raw = find_routes(start_coord, end_coord, day=day, time=time, token=token, walk_speed=walk_speed, min_transfer_time=min_transfer_time, amount=amount)
    image = routes_graphical_representation(raw)
    show_image_pil_upper_left(image)


def main(dest):
    locations = {"GYM_CENTER": GYM_CENTER, "AALTO": AALTO, "PRISMA": PRISMA}
    get_routes(HOME, locations[str(dest)])


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print("Requires exactly 1 argument")
