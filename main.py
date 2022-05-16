from typing import Optional
from fastapi import FastAPI, status, Response, HTTPException
from pydantic import BaseModel
from random import randrange

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True  # default to True, making this field optional in the POST request
    rating: Optional[int] = None  # fully optional field, defaults to None if not provided


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


@app.get("/posts")
def get_posts():
    return {"data": my_posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    post_dict = post.dict()
    post_dict['id'] = randrange(0, 10921295)
    my_posts.append(post_dict)
    return {"data": post_dict}


@app.get("/posts/{post_id}")
def get_post(post_id: int):
    post = find_post(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {post_id} was not found")
    return {"post detail": post}


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int):
    # find index in array containing the required post id
    index = find_post_index(post_id)

    if index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {post_id} does not exist")

    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


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

