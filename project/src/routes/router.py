from fastapi import APIRouter

route = APIRouter(prefix=config("ROUTERS_PREFIX"))


# @route.post("/register")
#
# @route.get("/contacts")
#
# @route.get("/count")
#
# @route.get("/contact/{_id}")
#
# @route.put("/edit/{_id}")
#
# @route.delete("/remove/{_id}")
#
# @route.get("/contacts/{letter}")
