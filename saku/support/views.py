# from django.shortcuts import 

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from support.maps import support_q_maps

# Create your views here.


class GeneralAdviceView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            q_maps_keys = support_q_maps.keys()
            for key in request.data.keys():
                if key not in q_maps_keys:
                    raise KeyError
            answer_values = [support_q_maps[key][str(request.data[key])] for key in q_maps_keys]
            final_value = sum(answer_values)

            # result = 0
            if final_value < 0:
                result = 0
            elif final_value <= len(support_q_maps) / 2:
                result = 1
            elif final_value  < len(support_q_maps):
                result = 2
            else:
                result = 3
            
            response = {
                "status": "success",
                "code": status.HTTP_200_OK,
                "data": {
                    "level": result
                }
            }

        except KeyError as e:
            response = {
                "status": "error",
                "code": status.HTTP_400_BAD_REQUEST,
                "message": "There is a problem with the data you have sent.",
                "data": []
            }

        return Response(response, status=response["code"])

