from fastapi import FastAPI, status, Response, HTTPException
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()


class Post(BaseModel):
    id: int
    title: str
    content: str
    published: bool = True  # default to True, making this field optional in the POST request


while True:
    try:
        conn = psycopg2.connect("dbname=fastapi user=postgres password=changeme123", cursor_factory=RealDictCursor)
        print("Connection successful")
        break
    except Exception as error:
        print("Connecting to database failed: ", error)
        time.sleep(3)


my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1},
            {"title": "favorite foods", "content": "I like ice cream", "id": 2}]


def find_post(post_id):
    for p in my_posts:
        if p['id'] == post_id:
            return p


def find_post_index(post_id):
    for i, p in enumerate(my_posts):
        if p['id'] == post_id:
            return i


@app.get("/")
def read_root():
    return {"message": "Hello World"}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    with conn.cursor() as cur:
        cur.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """,
                    (post.title, post.content, post.published))
        new_post = cur.fetchone()
    conn.commit()
    return {"data": new_post}


@app.get("/posts")
def get_posts():
    with conn.cursor() as cur:
        cur.execute("""SELECT * FROM posts""")
        posts = cur.fetchall()
    return {"data": posts}


@app.get("/posts/{post_id}")
def get_post(post_id: int):
    post = find_post(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {post_id} was not found")
    return {"post detail": post}


@app.put("/posts/{post_id}")
def update_post(post_id: int, post: Post):
    index = find_post_index(post_id)

    if index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {post_id} does not exist")

    post_dict = post.dict()
    post_dict['id'] = post_id
    my_posts[index] = post_dict
    return {"data": post_dict}


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int):
    # find index in array containing the required post id
    index = find_post_index(post_id)

    if index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {post_id} does not exist")

    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
