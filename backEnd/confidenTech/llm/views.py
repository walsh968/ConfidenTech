from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import AIResponseLog
from .service import confidence_and_answer
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def get_confidence_score(request):
    """
    Take in a prompt from the front end, and retrieve and AI output and confidence score
    """
    if request.method == 'POST':
        prompt = request.data.get('text', '')

        if not prompt:
            return Response({'error': 'Prompt is empty'}, status=status.HTTP_400_BAD_REQUEST)
    
        # Get full result dictionary from service.py
        result = confidence_and_answer(prompt)         

        # Set up log to MongoDB here
        log_entry = AIResponseLog.objects.create(
            input_query=prompt,
            model_a=result.get("model_a"),
            model_b=result.get("model_b"),
            embed_model=result.get("embed_model"),
            model_a_confidence=result.get("a_self"),
            model_b_confidence=result.get("b_self"),
            agreement_score=result.get("agreement"),

            # Determine which confidence to use as the final one
            final_confidence=(
                result.get("a_conf_pct")
                if result.get("best_model") == result.get("model_a")
                else result.get("b_conf_pct")
            ),
            
            best_model=result.get("best_model"),
            best_answer=result.get("best_answer")
        )

        # Return the simplified response to frontend
        return Response({
            'confidence': log_entry.final_confidence,
            'answer': log_entry.best_answer
        }, status=status.HTTP_200_OK)

    return Response({'message': 'Success'}, status=status.HTTP_200_OK)

from llm.service import confidence_and_answer
@api_view(['POST'])
@permission_classes([AllowAny])
def get_confidence_score_and_answer(request):
    '''
    Take in user input and feed it to the confidence algorithm to get the confidence score
    '''
    text = request.data.get('text')

    score, answer = confidence_and_answer(text)

    return Response({
        'score': score,
        'answer': answer
    }, status=status.HTTP_200_OK)
    