import json
import responses


@responses.activate
def test_post_with_json_parameters(client):

    remote_url = 'http://a.b.com/xyz:999'
    response_status_code = 299
    response_content_type = 'aaa-bbb/ccc-ddd'

    def _callback(req):
        resp_body = {
            'got-this': json.loads(req.body)
        }
        return (
            response_status_code,
            {},
            json.dumps(resp_body)
        )

    responses.add_callback(
        responses.POST,
        remote_url,
        content_type=response_content_type,
        callback=_callback)

    request_payload = {
        'url': remote_url,
        'parameters': {
            'a': 1,
            'b': 'xyz'
        }
    }

    rv = client.post(
        "/json-proxy/post",
        data=json.dumps(request_payload),
        headers={'content-type': 'application/json'}
    )

    assert rv.status_code == response_status_code
    assert rv.content_type == response_content_type
    rsp_json = json.loads(rv.data.decode('utf-8'))
    assert rsp_json['got-this'] == request_payload['parameters']
