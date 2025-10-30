// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'stream_data.model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

StreamData _$StreamDataFromJson(Map<String, dynamic> json) => StreamData(
      away: json['away'] as bool,
    )
      ..switch1Content = (json['left_content'] as num?)?.toInt()
      ..switch2Content = (json['right_content'] as num?)?.toInt();

Map<String, dynamic> _$StreamDataToJson(StreamData instance) =>
    <String, dynamic>{
      'away': instance.away,
      'left_content': instance.switch1Content,
      'right_content': instance.switch2Content,
    };
