import make_request
import model

data = make_request.get_league_data(10826)
tournament = model.League(**data)
# tournament.insert_to_db()
print()

#10826 Epicenter
#9870 TI 8
# 10749 TI 9