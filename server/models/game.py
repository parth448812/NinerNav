"""Contains functions for game functions, such as logging scores and getting level data."""
from sqlalchemy import desc, func
from .models import db, User, Map, Score
from . import user as user_model

def get_user_scores(user: User|str|int) -> list[Score]|None:
    """Gets all of the specified user's scores.

    Args:
        user: A User object, the username of a user, or a user's id

    Returns:
        A list of all scores belonging to the specified user
    """
    # Ensure the user is a User
    user_id = user_model.convert_user_to_id(user)
    if user_id == None:
        return None

    return Score.query.filter(Score.userid == user_id).all()

def get_user_scores_by_map(user: User|str|int, map: Map|str|int) -> list[Score]|None:
    """Gets all of the specified user's scores for a specific map.

    Args:
        user: A User object, the username of a user, or a user's id
        map: A Map object, the name of a map, or a map's id

    Returns:
        A list of all scores belonging to the specified user
    """
    # Ensure the user is a User
    user_id = user_model.convert_user_to_id(user)
    if user_id == None:
        return None

    # Get the map's id
    map_id = _convert_map_to_obj(map)
    if map_id == None:
        return None

    return Score.query.filter(Score.userid == user_id, Score.mapid == map_id).all()

def get_top_user_score(user: User|str|int) -> int|None:
    """Gets the user's top score.

    Args:
        user: A User object, the username of a user, or a user's id

    Returns:
        The user's top score or None if the user does not exist or they have no scores
    """
    user_id = user_model.convert_user_to_id(user)
    if user_id == None:
        return None

    return db.session.query(func.max(Score.score)).filter(Score.userid == user_id).first()[0]

def get_avg_user_score(user: User|str|int) -> float|None:
    """Gets the user's average score.

    Args:
        user: A User object, the username of a user, or a user's id

    Returns:
        The user's average score or None if the user does not exist or they have no scores
    """
    user_id = user_model.convert_user_to_id(user)
    if user_id == None:
        return None

    return db.session.query(func.avg(Score.score)).filter(Score.userid == user_id).first()[0]

def get_top_scores(num_scores: int=10) -> list[tuple[User, Map, Score]]:
    """Gets the top num_scores scores.

    Args:
        num_scores: The number of scores that should be retrieved
    """
    return db.session.query(User, Map, Score
        ).filter(
            User.id == Score.userid, Map.id == Score.mapid
        ).order_by(
            desc(Score.score)
        ).limit(num_scores).all()

def register_score(user: User|str|int, map: Map|str|int, score: int) -> Score:
    """Register a new score for a given user on a given map.

    Args:
        user: A User object, the username of a user, or a user's id
        map: A Map object or the name of a map
        score: The score that the user achieved on the given map

    Returns:
        The newly registered score
    """
    user_id = user_model.convert_user_to_id(user)
    map_id = _convert_map_to_obj(map)

    if user_id == None or map_id == None:
        return None

    try:
        new_score = Score(userid=user_id, mapid=map_id, score=score)
        db.session.add(new_score)
        db.session.commit()
    except:
        db.session.rollback()
        raise

    return new_score

def get_map_by_name(map_name: str) -> Map|None:
    """Gets a map by its name if it exists.

    Args:
        map_name: The name of the map to fetch

    Returns:
        The map with the given name if such a map exists
        None if no map has the given name
    """
    return Map.query.filter(Map.name == map_name).first()

def get_map_by_id(map_id: int) -> Map|None:
    """Gets a map by its id if it exists.

    Args:
        map_id: The id of the map to fetch

    Returns:
        The map with the given id if such a map exists
        None if no map has the given id
    """
    return Map.query.filter(Map.id == map_id).first()

def get_map_by_difficulty(difficulty: int, index: int) -> Map|None:
    """Gets the index-th map with the specified difficulty.

    Args:
        difficulty: The difficulty of the map, as seen in the Difficulty enum in game_controller
        index: The index of the map with the given difficult that should be selected, 0-indexed
    """
    res = Map.query.filter(Map.difficulty == difficulty).all()
    if res == None or len(res) <= index:
        return None
    return res[index]

def get_map_count() -> list[int]:
    res = db.session.query(func.count(Map.difficulty)).group_by(Map.difficulty).all()
    return [e[0] for e in res]

def _convert_map_to_obj(map: Map|str|int) -> Map|None:
    """Given either a Map or a map name, convert it to a Map.

    Args:
        map: A Map object, the name of a map, or a map's id

    Returns:
        The corresponding Map object or None if no such map exists
    """
    if type(map) == str:
        map = get_map_by_name(map)
        if map != None:
            return map.id
    elif type(map) == Map:
        return map.id

    return map